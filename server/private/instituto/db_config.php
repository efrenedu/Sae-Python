<?php

//Verify if the Tables are Corrupt
function verify_integrity_tables($conexion,$base_name,$list_tables){
      $corrupted_tables="";
      $all_ok=true;
	  for ($i=0;$i<count($list_tables);$i++){
          $tabl=$list_tables[$i];
          $query="CHECK TABLE {$base_name}.{$tabl};";
          try{
			 $res_query=mysqli_query($conexion,$query);
			 $res_table=false;
			 while($temp_dat=mysqli_fetch_array($res_query)){
      	         $msg_type=$temp_dat[2];
                 $msg_text=$temp_dat[3];
                 if($msg_type=="status" && $msg_text=="OK"){
                    $res_table=True;
			     }
             }
			 if($res_table==false){
				 $all_ok=False;
				 if($corrupted_tables==""){
					  $corrupted_tables=$tabl;
				 }
				 else{
                     $corrupted_tables=$corrupted_tables." , ".$tabl;
				 }
			 }
		  }
         catch(mysqli_sql_exception $e){
             $err=$e->getCode().":".$e->getMessage();
	         return ["status"=>"Error","message"=>$err];
         }
     }
     if($all_ok==False){
		 return ["status"=>"Error","message"=>"Las Tablas {$corrupted_tables} Estan Corruptas"];
    }
	return["status"=>"Succes","message"=>""];
}

//Add Additional Indexs to Tables
function set_indexs_db($conexion,$nomb_base,$indexs_dat){
    foreach($indexs_dat as $key=>$val){
		$tabl="{$nomb_base}.{$key}";
		$dat_index=$indexs_dat[$key];
		$field=$dat_index[1];
        $id_index=$dat_index[0];
		try{
			$query=" ALTER TABLE {$tabl} ADD INDEX {$id_index}({$field});";
            mysqli_query($conexion,$query);
		}
		catch(mysqli_sql_exception $e){
             $err=$e->getCode().":".$e->getMessage();
	         return ["status"=>"Error","message"=>$err];
        }
    }
	return["status"=>"Succes","message"=>""];
}

//Build DataBase and Tables
function build_db($conexion,$nomb_base,$list_tables,$fields_tables,$primary_keys){
	 try{
		   $res_json=["status"=>"success","message"=>"DataBase Construida Exitosamente"];
	       $query="CREATE DATABASE {$nomb_base};";
		   $res=mysqli_query($conexion,$query);
           for ($i=0;$i<count($list_tables);$i++){
              $name_tabl=$list_tables[$i];
              $query="CREATE TABLE {$nomb_base}.{$name_tabl}(";
              $fields_target=$fields_tables[$name_tabl];
              $foreign_values=array();
              for ($j=0;$j<count($fields_target);$j++){
                  $target=$fields_target[$j];
                  $name_field=$target["name"];
                  $fld_type=$target["field-type"];
				  $end_char="";
				  if($j<count($fields_target)-1){
					  $end_char=" , ";
				  }
                  $primary_key="";
				  $foreign_str_len=strlen("FOREIGN KEY");
                  if($fld_type=="PRIMARY KEY"){
                     $primary_key=$fld_type;
			      }
                  else if(substr($fld_type,0,$foreign_str_len)=="FOREIGN KEY"){
                      $foregein_dat=explode(":",$fld_type);
                      $foregein_reffld=$foregein_dat[1];
                      $foregein_tabl=explode("-",$foregein_dat[0])[1];                 
                      $foreign_values[]="FOREIGN KEY ({$name_field}) REFERENCES {$foregein_tabl}({$foregein_reffld})";
				  }
				  $temp_query=" {$name_field} VARCHAR(255) {$primary_key}{$end_char}";
				  $query=$query.$temp_query;
		      }
              if(count($foreign_values)>0){
			       for ($j=0;$j<count($foreign_values);$j++){
					  $query=$query." , {$foreign_values[$j]}";
				   }
		      }	
              $query=$query." );";			  
		      mysqli_query($conexion,$query);
	       }
		   return ["status"=>"Succes","message"=>"Base de Datos Iniciada Exitosamente"];
	 }
     catch(mysqli_sql_exception $e){
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
     }			
}


//get the primary keys of the DB as a Dictionary
function get_primary_fields($scheme_data){
	$res=array();
	$tables_list=$scheme_data["tables_names"];
	$fields_tables=$scheme_data["fields_tables"];
	for($i=0;$i<count($tables_list);$i++){
		$tabl_target=$tables_list[$i];
		$fields_target=$fields_tables[$tabl_target];
        for($j=0;$j<count($fields_target);$j++){
			$fld=$fields_target[$j];
			$fld_type=$fld["field-type"];
			if($fld_type=="PRIMARY KEY"){
				$res[$tabl_target]=$fld["name"];
				$j=count($fields_target);
			}
		}
	}
	return $res;
}

//set the Seed Data On DataBase if Not Exists
function set_seed_data($conexion,$nomb_base,$seed_data,$primary_keys){
        date_default_timezone_set('America/Caracas');
        $fecha=strval(date("d-m-Y"));
	    foreach($seed_data as $tabl=>$data_list){
		   $primary_key_target=$primary_keys[$tabl];
		   for ($i=0;$i<count($data_list);$i++){
			  $data_tabl=$data_list[$i];
              $primary_val=$data_tabl[$primary_key_target];
			  $exist_dat=id_exist($conexion,$nomb_base,$tabl,$primary_key_target,$primary_val);
			  if($exist_dat["status"]=="Error"){
				  return $exist_dat;
			  }
			  if($exist_dat["message"]=="True"){
				 continue;
			  }
			  foreach($data_tabl as $field=>$val_field){
				   if($val_field=="Calculate_date"){
					   $data_tabl[$field]=$fecha;
				   }
				   if(gettype($val_field)=="array"){
					   $tabl_temp=$val_field[0];
					   $primarkey_temp=$primary_keys[$tabl_temp];
					   $temp_dat=$val_field[1];
					   $id_dat=generate_id($conexion,$nomb_base,$tabl_temp,$primarkey_temp);
					   if($id_dat["status"]=="Error"){
						  return $id_dat;
					   }
					   $temp_dat[$primarkey_temp]=$id_dat["message"]; 
					   foreach($temp_dat as $temp_field=>$temp_fieldVal){
						   if($temp_fieldVal=="Calculate_date"){
							   $temp_dat[$temp_field]=$fecha;
						   }
					   }
					   $res=add_data($conexion,$nomb_base,$tabl_temp,$temp_dat,true);
					   if($res["status"]=="Error"){
						   return $res;
					   }
					   $data_tabl[$field]=$temp_dat[$primarkey_temp]; 
				   }
			  }
              $res_add=add_data($conexion,$nomb_base,$tabl,$data_tabl,true,true);			  
		      if($res_add["status"]=="Error"){
				  return $res_add;
			  }
		   }
		}
		return ["status"=>"Succes","message"=>"seed data Succes"];
}

//Verify if the Id Exists
function id_exist($conexion,$nomb_base,$tabl,$id_field,$id_name){
    mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	$field_dat=get_fields([$tabl]);
	if($field_dat["status"]=="Error"){
		return $field_dat;
	}
	$list_fields=$field_dat["message"];
	$exist=false;
	for($i=0;$i<count($list_fields);$i++){
		if($list_fields[$i]==$id_field){
			$exist=true;
			$i=count($list_fields);
		}
	}
	if($exist==false){
		return ["status"=>"Error","message"=>"El campo Solicitado {$id_field} es Inexistente en la Tabla Indicada{$tabl}"];
	}
	$query="SELECT {$id_field} FROM {$nomb_base}.{$tabl} WHERE {$id_field}=?;";
    try{
	     $statment=mysqli_prepare($conexion,$query);
         mysqli_stmt_bind_param($statment,"s",$id_name); 
		 mysqli_stmt_execute($statment);
         $res=$statment->get_result();
         $dict_res=$res->fetch_assoc();
         $statment->close();
         if($dict_res!=null){
			 return ["status"=>"Success","message"=>"True"];
		 } 
		 return ["status"=>"Success","message"=>"False"];
	  }
	  catch(mysqli_sql_exception $e){
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
     }	
}

//generate a Id based on the numbers of Registers on the Table
function generate_id ($conexion,$nomb_base,$tabl,$nomb_field){
	mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	$num_rows=0;
	if($conexion==null || $conexion==false){
		return ["status"=>"Error","message"=>"Conexion Invalida"];
	}
	$field_dat=get_fields([$tabl]);
	if($field_dat["status"]=="Error"){
		mysqli_rollback($conexion);
		return $field_dat;
	}
	$list_fields=$field_dat["message"];
	$exist=false;
	for($i=0;$i<count($list_fields);$i++){
		if($list_fields[$i]==$nomb_field){
			$exist=true;
			$i=count($list_fields);
		}
	}
	if($exist==false){
		mysqli_rollback($conexion);
		return ["status"=>"Error","message"=>"El campo Solicitado {$nomb_field} es Inexistente en la Tabla Indicada{$tabl}"];
	}
	try{
		$query="SELECT COUNT(*) FROM {$nomb_base}.{$tabl};";
		$data=mysqli_query($conexion,$query);
		if( mysqli_data_seek($data,0)){
           $row=mysqli_fetch_row($data);
	       $num_rows=(int)$row[0];
	    }
        if($num_rows==0){
			return ["status"=>"Success","message"=>"0"];
		}
		for($i=0;$i<$num_rows;$i++){
			$exist_dat=id_exist($conexion,$nomb_base,$tabl,$nomb_field,strval($i));
			if($exist_dat["status"]=="Error"){
				mysqli_rollback($conexion);
				return $exist_dat;
			}
			if($exist_dat["message"]=="False"){
				return ["status"=>"Success","message"=>strval($i)];
			}
		}
		return ["status"=>"Success","message"=>strval($num_rows)];
    }
	catch(mysqli_sql_exception $e){
		 mysqli_rollback($conexion);
		 $err=$e->getCode().":".$e->getMessage();
	     return ["status"=>"Error","message"=>$err];
	}
}


//verify if is Neccesary Build the DataBase
function verify_db(){
	$conex_data=get_conexion();
	mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	if($conex_data["response"]<0){
		 return["status"=>"Error","message"=>"Error Conectando con el Servidor"];
	}
	//get scheme data
	$temp_scheme=get_scheme_dat();
	if($temp_scheme["status"]=="Error"){
		return $temp_scheme;
	}
	$dat_scheme=$temp_scheme["message"];
	$tables=$dat_scheme["tables_names"];
	$fields_tables=$dat_scheme["fields_tables"];
	$add_indexs=$dat_scheme["add_indexs"];
	$seed_data=$dat_scheme["seed_data"];
	$primary_fields=get_primary_fields($dat_scheme);
	
	//verify if Exists Data Base
	$conexion=$conex_data["conector"];
	$nomb_base=$conex_data["db"];
	$query="SHOW DATABASES;";
	$res=mysqli_query($conexion,$query);
	$exists=false;
    while($temp_dat_db=mysqli_fetch_array($res)){
      	if($temp_dat_db[0]==$nomb_base){
	      $exists=true;
        }
    }
    if($exists==true){
	   $res_integrity=verify_integrity_tables($conexion,$nomb_base,$tables);
	   if($res_integrity["status"]=="Error"){
		  return $res_integrity; 
	   }
	   $dat_cond=["conditions"=>["id_nombre"],"values"=>["10"],"conectors"=>["and"],"verify_type"=>["="]];
	   return set_seed_data($conexion,$nomb_base,$seed_data,$primary_fields);
	}
	//Build Data Base
	$res_db= build_db($conexion,$nomb_base,$tables,$fields_tables,$primary_fields);
	if($res_db["status"]=="Error"){
		return $res_db;
	}
    $res_indexs=set_indexs_db($conexion,$nomb_base,$add_indexs);
	if($res_indexs["status"]=="Error"){
		return ["status"=>"Error","message"=>"Error al Agregar Indices a la Base de Datos"];;
	}
	return set_seed_data($conexion,$nomb_base,$seed_data,$primary_fields);
}

//delete the data of a Table*/
function delete_data($conexion,$base_name,$tabl,$cond_dat,$join_dat,$do_commit=false){
	if($conexion==null || $conexion==false){
		return ["status"=>"Error","message"=>"Conexion Invalida"];
	}
	$query="";
	
	$list_tablesQuery=[$tabl];
	$join_conds_list=array();
	if($join_dat!=null){
		foreach($join_dat as $tabl_join=>$data_table_join){
			$list_tablesQuery[]=$tabl_join;
			$cond_join=$data_table_join["Conditions_join"];
			if($cond_join!=null){
			   $join_conds_list[$tabl_join]=$cond_join;
			}
		}
	}
	$fields_dat=get_fields($list_tablesQuery);
	$values_list=array();
	if($fields_dat["status"]=="Error"){
		mysqli_rollback($conexion);
		return $fields_dat;
	}
	$list_fields=$fields_dat["message"];
	$list_alias=$fields_dat["extra_message"];
	$alias_main_tabl=$list_alias[$tabl];
	$alias_delete_str="";
	if(count($list_tablesQuery)>0){
		for($i=0;$i<count($list_tablesQuery);$i++){
		   $target_alias=$list_alias[$list_tablesQuery[$i]];
		   $alias_delete_str.=$target_alias;
		   if($i<count($list_tablesQuery)-1){
			    $alias_delete_str.=" , ";
		   }  
	    }
	}
	
		
	$query="DELETE {$alias_delete_str} FROM {$base_name}.{$tabl} {$alias_main_tabl}";
	if($join_dat!=null){
		 $res_join=add_joins($query,$list_fields,$join_dat,$base_name,$list_alias);
		 if($res_join["status"]=="Error"){
			 mysqli_rollback($conexion);
			 return $res_join;
		 }
		 $query=$res_join["message"];
	}
	$total_conds=array();
	if($cond_dat!=null){
		
       if(count($cond_dat)>0){
		   $total_conds[$tabl]=$cond_dat;
		   $values_list=$cond_dat["conditions_Values"];
	
	   }
	}
	foreach($join_conds_list as $cond_tabl_join=>$cond_dat_join){
		if(count($cond_dat_join)>0){
			$total_conds[$cond_tabl_join]=$cond_dat_join;
		}
	}
	if(count($total_conds)<=0){
	   mysqli_rollback($conexion);
	   return ["status"=>"Error","message"=>"Falta Condicion para Borrar"];
	}
	
	$res_conds=add_conditions($query,$list_fields,$total_conds,$list_alias);
	if($res_conds["status"]=="Error"){
		 mysqli_rollback($conexion);
		 return $res_conds;
	}
	mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	mysqli_autocommit($conexion,FALSE);
	  
	try{
	   $query=$res_conds["message"];
	   $query=$query.";";
       $str_types=str_repeat("s",count($values_list));
       $statment=mysqli_prepare($conexion,$query);
       mysqli_stmt_bind_param($statment,$str_types,...$values_list);
	   mysqli_stmt_execute($statment);
       $statment->close();
	   if($do_commit==true){
		    mysqli_commit($conexion);
	   }
	   mysqli_autocommit($conexion,TRUE);
	   return ["status"=>"Success","message"=>"Data Actualizada"];
	}
	catch(mysqli_sql_exception $e){
		  mysqli_rollback($conexion);
		  mysqli_autocommit($conexion,TRUE);
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
    }
	
}

//update the data of a Table
function update_data($conexion,$base_name,$tabl,$fields_update,$cond_dat,$join_dat,$do_commit=false){
	if($conexion==null || $conexion==false){
		return ["status"=>"Error","message"=>"Conexion Invalida"];
	}
	$query="";
	$list_tablesQuery=[$tabl];
	$join_query_fields=array();
	$join_conds_list=array();
	if($join_dat!=null){
		foreach($join_dat as $tabl_join=>$data_table_join){
			$join_query_fields[$tabl_join]=$data_table_join["query_field"];
			$cond_join=$data_table_join["Conditions_join"];
			if($cond_join!=null){
			   $join_conds_list[$tabl_join]=$cond_join;
			}
			$list_tablesQuery[]=$tabl_join;
		}
	}
	$fields_dat=get_fields($list_tablesQuery);
	$values_list=array();
	if($fields_dat["status"]=="Error"){
		mysqli_rollback($conexion);
		return $fields_dat;
	}
	$list_fields=$fields_dat["message"];
	$list_alias=$fields_dat["extra_message"];
	$main_alias_name=$list_alias[$tabl];
	$total_fields=array();
	$query="UPDATE {$base_name}.{$tabl} {$main_alias_name}";
	if($join_dat!=null){
		 $res_join=add_joins($query,$list_fields,$join_dat,$base_name,$list_alias);
		 if($res_join["status"]=="Error"){
			 mysqli_rollback($conexion);
			 return $res_join;
		 }
		 $query=$res_join["message"];
	}
	if(count($fields_update)>0){
		$total_fields[$tabl]=$fields_update;
	}
	foreach($join_query_fields as $target_join=>$target_join_data){
		if(count($target_join_data)>0){
		    $total_fields[$target_join]=$target_join_data;	
		}
	}
	if(count($total_fields)<=0){
		mysqli_rollback($conexion);
		return ["status"=>"Error","message"=>"No Existen Campos Actualizar"];
	}
	$query=$query." SET ";
	$first_field=true;
	foreach($total_fields as $target_tabl=>$fields_table){
		$alias_table=$list_alias[$target_tabl];
		$text_alias="";
		if($alias_table!=""){
			$text_alias="{$alias_table}.";
		}
		foreach($fields_table as $target_field=>$value_field){
			$init_char=" , ";
			if($first_field==true){
				$init_char="";
				$first_field=false;
			}
            $exist_field=false;
			for($i=0;$i<count($list_fields);$i++){
			    if($target_field==$list_fields[$i]){
				    $exist_field=true;
				    $i=count($list_fields);
			    }
		    }
		    if($exist_field==false){
				 mysqli_rollback($conexion);
			     return ["status"=>"Error","message"=>"Campos Solicitados Invalidos"];
		    }
            $query=$query.$init_char.$text_alias.$target_field."=?";
		    $values_list[]=$value_field;
		}		
	}
	
	$total_conds=array();
	if($cond_dat!=null){
		if(count($cond_dat)>0){
			$total_conds[$tabl]=$cond_dat;
			$list_conds=$cond_dat["conditions_Values"];
	        foreach ($list_conds as $key=>$value){
		        $values_list[]=$value;
	        }
		}
	}
	foreach($join_conds_list as $tabl_join=>$dat_cond_join){
		if(count($dat_cond_join)>0){
		    $total_conds[$tabl_join]=$dat_cond_join;
            $values_list_join=$dat_cond_join["conditions_Values"];
		    for($i=0;$i<count($values_list_join);$i++){
				 $values_list[]=$values_list_join[$i];
			 }	
		}
	}
	if(count($total_conds)<=0){
		mysqli_rollback($conexion);
		return ["status"=>"Error","message"=>"Falta Condicion para Actualizar"];

	}
	$res_conds=add_conditions($query,$list_fields,$total_conds,$list_alias);
	if($res_conds["status"]=="Error"){
		 mysqli_rollback($conexion);
		 return $res_conds;
	}
	mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	mysqli_autocommit($conexion,FALSE);
	   
	try{
	   $query=$res_conds["message"];
	   $query=$query.";";
       $str_types=str_repeat("s",count($values_list));
       $statment=mysqli_prepare($conexion,$query);
	   if($statment==false){
		   mysqli_rollback($conexion);
		   return ["status"=>"Error","message"=>"Imposible Crear Query para {$query}"]; 
	   }
       mysqli_stmt_bind_param($statment,$str_types,...$values_list);
	   mysqli_stmt_execute($statment);
       $statment->close();
	   if($do_commit==true){
			mysqli_commit($conexion);
	   }
	   mysqli_autocommit($conexion,TRUE);
	 
	   return ["status"=>"Success","message"=>"Data Actualizada"];
	}
	catch(mysqli_sql_exception $e){
		  mysqli_rollback($conexion);
		  mysqli_autocommit($conexion,TRUE);
	 
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
    }
	
}
//get the data of requireds tables as dict/Associative Array or list/Array
function get_data($conexion,$base_name,$tabl,$fields,$cond_dat,$join_dat,$as_dict=false){
	if($conexion==null || $conexion==false){
		return ["status"=>"Error","message"=>"Conexion Invalida"];
	}
	$query="";
	$list_tablesQuery=[$tabl];
	$join_query_fields=array();
	$join_conds_list=array();
	if($join_dat!=null){
		foreach($join_dat as $tabl_join=>$data_table_join){
			$join_query_fields[$tabl_join]=$data_table_join["query_field"];
			$cond_join=$data_table_join["Conditions_join"];
			if($cond_join!=null){
			   $join_conds_list[$tabl_join]=$cond_join;
			}
			$list_tablesQuery[]=$tabl_join;
		}	
	}
	$fields_dat=get_fields($list_tablesQuery);
	$values_list=array();
	if($fields_dat["status"]=="Error"){
		return $fields_dat;
	}
	$list_fields=$fields_dat["message"];
	$list_alias=$fields_dat["extra_message"];
	$alias_main_tabl=$list_alias[$tabl];
	
	if(count($fields)<=0 && count($join_query_fields)<=0){
		if($join_dat!=null){
			return ["status"=>"Error","message"=>"Debe Especificar los Campos cuando usa Join en Una Consulta"];
		}
		$query="SELECT * FROM {$base_name}.{$tabl}";
	}
	else{
		$query="SELECT ";
		if(count($fields)>0){
		   $total_fields[$tabl]=$fields;
		}
		
		foreach($join_query_fields as $tablJoin_target=>$fieldsJoin_target){
			if(count($fieldsJoin_target)>0){
				$total_fields[$tablJoin_target]=$fieldsJoin_target;
			}
		}
		$first_field=true;
		foreach($total_fields as $tabl_target=>$fields_target){
			$alias_tabl=$list_alias[$tabl_target];
			$alias_text="";
			if($alias_tabl!=""){
				$alias_text="{$alias_tabl}.";
			}
			for($i=0;$i<count($fields_target);$i++){
				$init_char=" , ";
			    $exist_field=false;
			    $target_field=$fields_target[$i];
			    for($j=0;$j<count($list_fields);$j++){
			       if($target_field==$list_fields[$j]){
				       $exist_field=true;
				       $j=count($list_fields);
			       }
		        }
		        if($exist_field==false){
			        return ["status"=>"Error","message"=>"Campos Solicitados Invalidos"];
		        }
			    if($first_field==true){
				    $init_char="";
					$first_field=false;
			    }
			    $query=$query.$init_char.$alias_text.$target_field;
				
			}
			
		}
		$query=$query." FROM {$base_name}.{$tabl} {$alias_main_tabl}";
	}
	if($join_dat!=null){
		 $res_join=add_joins($query,$list_fields,$join_dat,$base_name,$list_alias);
		 if($res_join["status"]=="Error"){
			 return $res_join;
		 }
		 $query=$res_join["message"];
	}
	
	if($cond_dat!=null){
		 $total_conds=array();
		 $total_conds[$tabl]=$cond_dat;
		 $values_list=$cond_dat["conditions_Values"];
		 foreach ($join_conds_list as $tabl_join=>$dat_cond_join){
			 $total_conds[$tabl_join]=$dat_cond_join;
			 $values_list_join=$dat_cond_join["conditions_Values"];
		     for($i=0;$i<count($values_list_join);$i++){
				 $values_list[]=$values_list_join[$i];
			 }
		 }
		 $res_conds=add_conditions($query,$list_fields,$total_conds,$list_alias);
		 if($res_conds["status"]=="Error"){
			 return $res_conds;
		 }
		 $query=$res_conds["message"];
	}
	$query=$query.";";
	$res=null;
	mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	try{
		 $data=array();
		 $statment=null;
		 if(count($values_list)>0){
		    $str_types=str_repeat("s",count($values_list));
            $statment=mysqli_prepare($conexion,$query);
            mysqli_stmt_bind_param($statment,$str_types,...$values_list);
		    mysqli_stmt_execute($statment);
            $res=$statment->get_result();
	     }
	     else{
			 $res=mysqli_query($conexion,$query); 
	    }
        while($extract=mysqli_fetch_array($res,MYSQLI_ASSOC)){
            if($as_dict==false){
				$temp=array();
                foreach($extract as $e){
			       $temp[]=$e;
		        }
                $data[]=$temp;
			}
			else{
			    $data[]=$extract;	
			}

        }
	    mysqli_free_result($res);
		if($statment!=null){
			$statment->close();
		}
		return ["status"=>"Succes","message"=>$data];
	}
	catch(mysqli_sql_exception $e){
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
    }
	
}

//add the required conditions to the query
function add_conditions($query,$list_fields,$total_conds,$alias_list){
	$query=$query." WHERE "; 
	$first_field=true;
	foreach($total_conds as $cond_tabl=>$cond_raw){
		$cond_list=$cond_raw["conditions_Names"];
	    $cond_values=$cond_raw["conditions_Values"];
        $cond_conectors=$cond_raw["condition_Types"];
	    $cond_verify_typ=$cond_raw["conditions_Verify"];
		if(array_key_exists($cond_tabl,$alias_list)==false){
		    return ["status"=>"Error","message"=>"Tablas de Condiciones No Validas"];
		}
		$target_alias=$alias_list[$cond_tabl];
		$alias_text="";
		if($target_alias!=""){
			$alias_text="{$target_alias}.";
		}
		$posibles_verificactions=array("=","!=","<",">");
		for($i=0;$i<count($cond_list);$i++){
			$next_cond=$cond_list[$i];
		    $next_val=$cond_values[$i];
		    $next_conector=strtoupper($cond_conectors[$i]);
		    $next_verification=$cond_verify_typ[$i];
		    $exist_field=false;
		    for($j=0;$j<count($list_fields);$j++){
			    if($next_cond==$list_fields[$j]){
				    $exist_field=true;
				    $j=count($list_fields);
			    }
		    }
		    if($exist_field==false){
			    return ["status"=>"Error","message"=>"Existen Nombre de Condiciones Invalidas"];
		    }
		    if($next_conector!="AND" && $next_conector!="OR"){
                return ["status"=>"Error","message"=>"Conectores de Condiciones Invalidos"];
		    }	
			$valid_verification_type=false;
			for($j=0;$j<count($posibles_verificactions);$j++){
				if($next_verification==$posibles_verificactions[$j]){
					$valid_verification_type=true;
					$j=count($posibles_verificactions);
				}
			}
            if($valid_verification_type==false){
               return ["status"=>"Error","message"=>"Tipos de Verificaciones Invalidos"];
		    }
	        if($first_field==true){
			     $next_conector="";
				 $first_field=false;
		    }
			
		    $next_cond="{$alias_text}{$next_cond}";
			$query=$query." {$next_conector} {$next_cond}{$next_verification}?";
  
		}
	}
   return ["status"=>"Succes","message"=>$query];
}

//add Join To the Query
function add_joins($query,$list_fields,$join_raw,$db,$alias_list){
	 $query_join="";
	 $first_join=true;
	 foreach ($join_raw as $tabl_join=>$data_table_join){
		 $alias_jointabl=$alias_list[$tabl_join];
		 $share_fields=$data_table_join["share_fields"];
		 $target_field=$share_fields["field"];
		 $reference_table=$share_fields["table_reference"];
		 if(array_key_exists($reference_table,$alias_list)==false){
			return ["status"=>"Error","message"=>"Tablas de Refrencia Invalidas en el Join "];
		 }
		 $alias_reference_table=$alias_list[$reference_table];

		 $exist_field=false;
		 for($i=0;$i<count($list_fields);$i++){
			if($target_field==$list_fields[$i]){
				$exist_field=true;
				$i=count($list_fields);
			}
		 }
		 if($exist_field==false){
			return ["status"=>"Error","message"=>"Existen Campos Invalidas en el Join "];
		 }
		 $query_join=$query_join." INNER JOIN {$db}.{$tabl_join} {$alias_jointabl}";
		 $query_join=$query_join." ON {$alias_jointabl}.{$target_field}={$alias_reference_table}.{$target_field}";
	 }
	 return ["status"=>"Succes","message"=>$query.$query_join];
}
//Verify if the Table is Empty
function is_empty($conexion,$bd,$tabl){
    mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	$res_tabl=verify_table($tabl);
	if($res_tabl["status"]=="Error"){
		return $res_tabl;
	}
	$query="SELECT COUNT(*) FROM {$bd}.{$tabl};";
	try{
	   $data=mysqli_query($conexion,$query);
	   $num_rows=0;
	   if( mysqli_data_seek($data,0)){
           $row=mysqli_fetch_row($data);
	       $num_rows=(int)$row[0];
	   }
        if($num_rows==0){
	      return ["status"=>"Success","message"=>"True"];
	    }
		return ["status"=>"Success","message"=>"False"];
	}
	catch(mysqli_sql_exception $e){
		$err=$e->getCode().":".$e->getMessage();
	    return ["status"=>"Error","message"=>$err];
	}
	
}
//get the scheme data of db
function get_scheme_dat(){
	$path_scheme=__DIR__."/bd_scheme.json";
    if(!file_exists($path_scheme)){
	   return["status"=>"Error","message"=>"Scheme File of Bd Not Found"];
    }
	$scheme_raw=file_get_contents($path_scheme);
    $dat_scheme=json_decode($scheme_raw,true);
	if(json_last_error()!=JSON_ERROR_NONE){
		 return["status"=>"Error","message"=>"Scheme File Bad Format"];
	}
	$json_raw=mb_convert_encoding($scheme_raw,"UTF-8","UTF-8, ISO-8859-1");
	$dat_scheme=json_decode($scheme_raw,true);
	
	return ["status"=>"Succes","message"=>$dat_scheme];
}

//Finsh Commit from a Big set of Updates
function finish_commit($conexion){
	if($conexion==null || $conexion==false){
		  return ["status"=>"Error","message"=>"Conexion Invalida"];
    }
	mysqli_commit($conexion);
}
//Verify if the Table Name is Valid 
function verify_table($tabl){
	 $temp_scheme=get_scheme_dat();
	 if($temp_scheme["status"]=="Error"){
	     	return $temp_scheme;
	 }
	 $dat_scheme=$temp_scheme["message"];
	 if(array_key_exists($tabl,$dat_scheme["fields_tables"])==false){
   	   return ["status"=>"Error","message"=>"tabla Inexistnte"];
	 }
	 return ["status"=>"Success","message"=>"Table OK"];
	
}

//Verify if the table exist and get the List of Fields of it
function get_fields($list_tabl){
	   
	  $temp_scheme=get_scheme_dat();
	  if($temp_scheme["status"]=="Error"){
	     	return $temp_scheme;
	  }
	  $dat_scheme=$temp_scheme["message"];
	  $alias_scheme=$dat_scheme["Alias_Tables"];
	  $alias_list=array();
	  $total_fields=array();
	  $for_join=false;
	  if(count($list_tabl)>1){
		  $for_join=true;
	  }
	  for ($i=0;$i<count($list_tabl);$i++){
		 if(array_key_exists($list_tabl[$i],$dat_scheme["fields_tables"])==false){
		    return ["status"=>"Error","message"=>"Existen Tablas Inexistnte"];
	     }
         $alias_list[$list_tabl[$i]]=$alias_scheme[$list_tabl[$i]];
         if($for_join==false){
            $alias_list[$list_tabl[$i]]="";
		 }			 
         $fields_temp=$dat_scheme["fields_tables"][$list_tabl[$i]];
	     for($j=0;$j<count($fields_temp);$j++){
		     $val=$fields_temp[$j]["name"];
		     $total_fields[]=$val; 
	     }  
	  }
      return ["status"=>"Success","message"=>$total_fields,"extra_message"=>$alias_list];  
}

/*add a Registrer(Row) to the Indicate Table*/
function add_data( $conexion,$bd,$tabl,$values,$dict_values=false,$do_commit=false,$multirow=false){

      if($conexion==null || $conexion==false){
		  return ["status"=>"Error","message"=>"Conexion Invalida"];
	  }
	  mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	  $query="INSERT INTO ".$bd.".".$tabl;
	  $values_list=array();
	  if($dict_values){
		 $res_fields=get_fields([$tabl]);
	     if($res_fields["status"]=="Error"){
			  mysqli_rollback($conexion);
		      return $res_fields;
	     }
	     $fields_list=$res_fields["message"];
		 $fields_str="";
		 $values_str="";
		 $values_list=array();
		 for($i=0;$i<count($fields_list);$i++){
			 $init_char=" , ";
			 if($i==0){
				 $init_char="";
			 }
			 $val_field=$fields_list[$i];
			 if(!array_key_exists($val_field,$values)){
				  mysqli_rollback($conexion);
				  return ["status"=>"Error","message"=>"Las Keys del Diccionario/Array Associativo no Coinciden con las de la Tabla"];
			 }
			 $fields_str=$fields_str.$init_char.$val_field;
			 $values_str=$values_str.$init_char."?";
			 $values_list[]=$values[$val_field];
		 }
		 $query=$query."({$fields_str}) VALUES ({$values_str});";
	  }
	  else{
		$res_tabl=verify_table($tabl);
        if($res_tabl["status"]=="Error"){
			mysqli_rollback($conexion);
            return $res_tabl;
		}			
		$values_list=$values;
		$values_str="";
		for($i=0;$i<count($values);$i++){
			 $init_char=" , ";
			 if($i==0){
				 $init_char="";
			 }
			 $values_str=$values_str.$init_char."?";
		 }
		$query=$query." VALUES ({$values_str});";  
	  }
	  mysqli_autocommit($conexion,FALSE);
	  try{
		 $str_types=str_repeat("s",count($values_list));
         $statment=mysqli_prepare($conexion,$query);
         mysqli_stmt_bind_param($statment,$str_types,...$values_list);
		 mysqli_stmt_execute($statment);
		 $statment->close();
		 if($do_commit==true){
			 mysqli_commit($conexion);
		 }
		 mysqli_autocommit($conexion,TRUE);
		 return ["status"=>"Success","message"=>"Data Added"];
	  }
	  catch(mysqli_sql_exception $e){
		  mysqli_rollback($conexion);
		  mysqli_autocommit($conexion,TRUE);
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
     }			
}
//reset a Table
function reset_table($conexion,$bd,$tabl){
   mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
   $res_tabl=verify_table($tabl);
   if($res_tabl["status"]=="Error"){
	   return false;
   }
   $request="TRUNCATE TABLE {$tabl};";
   try{
	   mysqli_query($conexion,$request);
	   return true;
   }
   catch(mysqli_sql_exception $e){
	   return false;
   }
	
}

//Set Foreign Check Value
function set_foreign_check($conexion,$bd,$value){
   mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
   $request="";
   if($value==false){
	  $request="SET FOREIGN_KEY_CHECKS = 0;"; 
   }
   else{
	   $request="SET FOREIGN_KEY_CHECKS = 1;"; 
   }
   try{
	   mysqli_query($conexion,$request);
	   return true;
   }
   catch(mysqli_sql_exception $e){
	  return false;
   }
}
//Restore the Data Base
function restore_bd($conexion,$bd,$abs_paths,$tables_send){
	if($conexion==null || $conexion==false){
	    yield ["statuts"=>"Error","message"=>"Conexion Invalida"];
	    return;	
	}
	
    mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	$temp_scheme=get_scheme_dat();
	if($temp_scheme["status"]=="Error"){
		yield $temp_scheme;
		return;
	}
	$dat_scheme=$temp_scheme["message"];
	
	
	$tables=$dat_scheme["tables_names"];
	if(count($abs_paths)!=count($tables) || count($tables_send)!=count($tables)){
		yield ["statuts"=>"Error","message"=>"El Numero de Tablas Recibido No Coincide con los de la Base de Datos"];
	    return;
	}
	
    if(set_foreign_check($conexion,$bd,false)==false){
		yield ["status"=>"Error","message"=>"Imposible desactivar Foreign Check"];
	    return;
	}
	mysqli_query($conexion,"SET UNIQUE_CHECKS=0;");
	
	$porcent=0;
	for($i=0;$i<count($abs_paths);$i++){
		$porcent=round((($i+1)/count($abs_paths))*100);
		yield[
		   "status"=>"Procesing",
		   "message"=>$porcent
	    ];
		$tabl_target=$tables_send[$i];
		if(reset_table($conexion,$bd,$tabl_target)==false){
			mysqli_rollback($conexion);
			$msg="Imposible Truncar Tabla {$tabl_target}";
			mysqli_query($conexion,"SET UNIQUE_CHECKS=1;");
			if(set_foreign_check($conexion,$bd,true)==false){
				$msg=$msg.", Error Reactivando Foreign Check";
			}
		    yield ["status"=>"Error","message"=>$msg];
			return;
		}
		$file_target=$abs_paths[$i];
		$temp_content=file_get_contents($file_target);
		if($temp_content==""){
			continue;
		}
		if(explode(";",$temp_content)<=1){
			continue;
		}
		$escape_path=str_replace("\\","/",$file_target);
		$request="LOAD DATA INFILE '{$conexion->real_escape_string($escape_path)}' REPLACE INTO TABLE {$tabl_target}";
		$request=$request." FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY'\\\\' LINES TERMINATED BY '\\r\\n' IGNORE 0 LINES;";   
		try{
             mysqli_query($conexion,$request);

		}
		catch(Exception $e){
			 $msg=$e->getMessage();
			 if(set_foreign_check(true)==false){
				     $msg=$msg.", Error Reactivando Foreign Check";
			  }
			  $conexion->query("SET UNIQUE_CHECKS=1;");
			  yield ["status"=>"Error","message"=>$msg];
			  return;
		      
		}
		
	}
	mysqli_query($conexion,"SET UNIQUE_CHECKS=1;");
	if(set_foreign_check($conexion,$bd,true)==false){
	    yield ["status"=>"Error","message"=>"Restauracion Realizada pero no se pudo Reactivar Foreign Check"];
	    mysqli_rollback($conexion);
		return;
	}
	$primary_fields=get_primary_fields($dat_scheme);
	$seed_data=$dat_scheme["seed_data"];
	$res_seed=set_seed_data($conexion,$bd,$seed_data,$primary_fields);
	if($res_seed["status"]=="Error"){
		mysqli_rollback($conexion);
		yield $res_seed;
		return;
	}
	mysqli_commit($conexion);
	yield ["status"=>"Success","message"=>"Restauracion de La Base de Datos Realizada Exitosamente"];
	
}

//Respaldthe Data Base
function respald_bd($conexion,$bd,$base_path){
	mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	$temp_scheme=get_scheme_dat();
	if($temp_scheme["status"]=="Error"){
		return $temp_scheme;
	}
	$dat_scheme=$temp_scheme["message"];
	$tables=$dat_scheme["tables_names"];
	$fields_tables=$dat_scheme["fields_tables"];
	$dat_tables=array();
	$ruta_respaldo=$base_path."respaldos".DIRECTORY_SEPARATOR;

    for($i=0;$i<count($tables);$i++){
		$tabl=$tables[$i];
		if(file_exists($ruta_respaldo.$tabl.".csv")){
			unlink($ruta_respaldo.$tabl.".csv");
		}
		$dat_target=get_data($conexion,$bd,$tables[$i],array(),null,null,true);
		if($dat_target["status"]=="Error"){
			return $dat_target;
		}
		$dat_target=$dat_target["message"];
		$path_file=$ruta_respaldo.$tabl.".csv";
		$path_file=str_replace("ñ","n",$path_file);
	            
	    $f_tabla=fopen($path_file,"w+");
		foreach($dat_target as $row){
            $linea=implode(";",$row);
			fwrite($f_tabla,$linea."\r\n");
		}
		 fflush($f_tabla);
		 fclose($f_tabla);	
	}
	
	$fecha=strval(date("d-m-Y"));
	$zip=new ZipArchive();
	$zip_server_name="respaldo-".$fecha.".zip";
	$nombre_zip=$ruta_respaldo.$zip_server_name;
	$files_contains=array();
	if($zip->open($nombre_zip,ZipArchive::CREATE |ZipArchive::OVERWRITE)){
		    $archivos=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($ruta_respaldo),RecursiveIteratorIterator::LEAVES_ONLY);
			foreach ($archivos as $f){
				if($f->isDir()){
					 continue;
				}
				$ruta_abs=$f->getRealPath();
				$nombre_file=basename($ruta_abs);
				$size_csv=strlen(".csv");
				if(substr($nombre_file,-$size_csv,$size_csv)==".csv"){
		            $files_contains[]=$ruta_abs;
                    $zip->addFile($ruta_abs,$nombre_file);					
			    }
			}
			if(count($files_contains)<=0){
				 return ["status"=>"Error","Message"=>"Can Not Build Backups CSV Files"];
			}
			
			
			$res=$zip->close();
			if(!$res){
				return ["status"=>"Error","message"=>"Can not Build Zip file of BackUp"];
			}
			foreach ($files_contains as $target_file){
				if(file_exists($target_file)){
					unlink($target_file);
				}
			}
			
	}
	return ["status"=>"Suceess","message"=>"Respaldo Realizado Exitosamente","data"=>"respaldos/".$zip_server_name,"filename"=>$zip_server_name];
}

//get the Connection to DB
function get_conexion(){
	
   $path_config=__DIR__."/config.json";
   if(!file_exists($path_config)){
	    return  array("response"=>-1,"data"=>"");
   }
   $config=json_decode(file_get_contents($path_config),true);
   $host=$config["host"];
   $user=$config["user"];
   $db=$config["db_name"];
   $pass=$config["password"];
   $conexion=mysqli_connect($host,$user,$pass);
   if (mysqli_connect_errno()) {
      return array("response"=>-2,"data"=>"");
  }
   mysqli_select_db($conexion,$db); 
   if (mysqli_connect_errno()) {
	 return array("response"=>-2,"data"=>"");
   }
   mysqli_set_charset($conexion,"utf8mb4");
   return array("response"=>0,"conector"=>$conexion,"db"=>$db);
}

?>