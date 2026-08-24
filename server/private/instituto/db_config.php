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
		 return ["status"=>"Error","message"=>"Las Tablas {$corrupteds_tables} Estan Corruptas"];
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
				return $exist_dat;
			}
			if($exist_dat["message"]=="False"){
				return ["status"=>"Success","message"=>strval($i)];
			}
		}
		return ["status"=>"Success","message"=>strval($num_rows)];
    }
	catch(mysqli_sql_exception $e){
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
		return temp_scheme;
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
	$res_db= build_db($conexion,$nomb_base,$tables,$fields_tables);
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
	$query="";
	$fields_dat=get_fields($tabl);
	$values_list=array();
	if($fields_dat["status"]=="Error"){
		return $fields_dat;
	}
	$list_fields=$fields_dat["message"];
	
	$query="DELETE FROM {$base_name}.{$tabl}";
	if($cond_dat==null){
		return ["status"=>"Error","message"=>"Falta Condicion para Actualizar"];
	}
	$values_list=$cond_dat["conditions_Values"];
	$res_conds=add_conditions($query,$list_fields,$cond_dat);
	if($res_conds["status"]=="Error"){
		 return $res_conds;
	}
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
	   return ["status"=>"Success","message"=>"Data Actualizada"];
	}
	catch(mysqli_sql_exception $e){
		  if($conexion!=null){
			  mysqli_rollback($conexion); 
		  }
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
    }
	
}

//update the data of a Table
function update_data($conexion,$base_name,$tabl,$fields_update,$cond_dat,$join_data,$do_commit=false){
	$query="";
	$fields_dat=get_fields($tabl);
	$values_list=array();
	if($fields_dat["status"]=="Error"){
		return $fields_dat;
	}
	$list_fields=$fields_dat["message"];
	
	$query="UPDATE {$base_name}.{$tabl} SET ";
	$first_field=true;
	foreach($fields_update as $target_field=>$value_field){
		$init_char=" , ";
		$exist_field=false;
		for($i=0;$i<count($list_fields);$i++){
			if($target_field==$list_fields[$i]){
				$exist_field=true;
				$i=count($list_fields);
			}
		}
		if($exist_field==false){
			 return ["status"=>"Error","message"=>"Campos Solicitados Invalidos"];
		}
		if($first_field==true){
			$first_field=false;
			$init_char="";
		}
		$query=$query.$init_char.$target_field."=?";
		$values_list[]=$value_field;
	}
	if($cond_dat==null){
		return ["status"=>"Error","message"=>"Falta Condicion para Actualizar"];
	}
    $list_conds=$cond_dat["conditions_Values"];
	foreach ($list_conds as $key=>$value){
		$values_list[]=$value;
	}
	$res_conds=add_conditions($query,$list_fields,$cond_dat);
	if($res_conds["status"]=="Error"){
		 return $res_conds;
	}
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
	   return ["status"=>"Success","message"=>"Data Actualizada"];
	}
	catch(mysqli_sql_exception $e){
		  if($conexion!=null){
			  mysqli_rollback($conexion); 
		  }
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
    }
	
}
//get the data of requireds tables as dict/Associative Array or list/Array
function get_data($conexion,$base_name,$tabl,$fields,$cond_dat,$join_dat,$as_dict=false){
	$query="";
	$fields_dat=get_fields($tabl);
	$values_list=array();
	if($fields_dat["status"]=="Error"){
		return $fields_dat;
	}
	$list_fields=$fields_dat["message"];
	
	if(count($fields)<=0){
		$query="SELECT * FROM {$base_name}.{$tabl}";
	}
	else{
		$query="SELECT ";
		for($i=0;$i<count($fields);$i++){
			$init_char=" , ";
			$exist_field=false;
			$target_field=$fields[$i];
			for($j=0;$j<count($list_fields);$j++){
			   if($target_field==$list_fields[$j]){
				   $exist_field=true;
				   $j=count($list_fields);
			   }
		    }
		    if($exist_field==false){
			    return ["status"=>"Error","message"=>"Campos Solicitados Invalidos"];
		    }
			if($i==0){
				$init_char="";
			}
			$query=$query.$init_char.$target_field;
		}
		$query=$query." FROM {$base_name}.{$tabl}";
	}
	if($cond_dat!=null){
		 $values_list=$cond_dat["conditions_Values"];
		 $res_conds=add_conditions($query,$list_fields,$cond_dat);
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
function add_conditions($query,$list_fields,$cond_raw){
	$query=$query." WHERE ";
    $cond_list=$cond_raw["conditions_Names"];
	$cond_values=$cond_raw["conditions_Values"];
    $cond_conectors=$cond_raw["condition_Types"];
	$cond_verify_typ=$cond_raw["conditions_Verify"];
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
        if($next_verification!="=" && $next_verification!="!="){
           return ["status"=>"Error","message"=>"Tipos de Verificaciones Invalidos"];
		}
	    if($i==0){
			 $next_conector="";
		}
		$query=$query." {$next_conector} {$next_cond}{$next_verification}?";
        		
   }
   return ["status"=>"Succes","message"=>$query];
}

//Verify if the Table is Empty
function is_empty($conexion,$bd,$tabl){
    mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	$temp_scheme=get_scheme_dat();
	if($temp_scheme["status"]=="Error"){
	     	return temp_scheme;
	}
	$dat_scheme=$temp_scheme["message"];
	if(array_key_exists($tabl,$dat_scheme["fields_tables"])==false){
		  return ["status"=>"Error","message"=>"tabla Inexistnte"];
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
	if(json_last_error()!==JSON_ERROR_NONE){
		$json_raw=mb_convert_encoding($scheme_raw,"UTF-8","UTF-8, ISO-8859-1");
		$dat_scheme=json_decode($scheme_raw,true);
	}
	return ["status"=>"Succes","message"=>$dat_scheme];
}

//Verify if the table exist and get the List of Fields of it
function get_fields($tabl){
	   
	  $temp_scheme=get_scheme_dat();
	  if($temp_scheme["status"]=="Error"){
	     	return temp_scheme;
	  }
	  $dat_scheme=$temp_scheme["message"];
	  if(array_key_exists($tabl,$dat_scheme["fields_tables"])==false){
		  return ["status"=>"Error","message"=>"tabla Inexistnte"];
	  }
	  $fields_temp=$dat_scheme["fields_tables"][$tabl];
      $fields_lists=array();
	  for($i=0;$i<count($fields_temp);$i++){
		 $val=$fields_temp[$i]["name"];
		 $fields_lists[]=$val; 
	  }
  return ["status"=>"Success","message"=>$fields_lists];  
}

/*add a Registrer(Row) to the Indicate Table*/
function add_data( $conexion,$bd,$tabl,$values,$dict_values=false,$do_commit=false){

	  mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	  $query="INSERT INTO ".$bd.".".$tabl;
	  $values_list=array();
	  if($dict_values){
		 $res_fields=get_fields($tabl);
	     if($res_fields["status"]=="Error"){
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
				  return ["status"=>"Error","message"=>"Las Keys del Diccionario/Array Associativo no Coinciden con las de la Tabla"];
			 }
			 $fields_str=$fields_str.$init_char.$val_field;
			 $values_str=$values_str.$init_char."?";
			 $values_list[]=$values[$val_field];
		 }
		 $query=$query."({$fields_str}) VALUES ({$values_str});";
	  }
	  else{
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
	  try{
		 $str_types=str_repeat("s",count($values_list));
         $statment=mysqli_prepare($conexion,$query);
         mysqli_stmt_bind_param($statment,$str_types,...$values_list);
		 mysqli_stmt_execute($statment);
		 $statment->close();
		 if($do_commit==true){
			 mysqli_commit($conexion);
		 }
		 return ["status"=>"Success","message"=>"Data Added"];
	  }
	  catch(mysqli_sql_exception $e){
		  if($conexion!=null){
			  mysqli_rollback($conexion); 
		  }
          $err=$e->getCode().":".$e->getMessage();
	      return ["status"=>"Error","message"=>$err];
     }			
}
//reset a Table
function reset_table($conexion,$bd,$tabl){
   mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
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
function restore_bd($conexion,$bd,$data_tables){
    mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	$temp_scheme=get_scheme_dat();
	if($temp_scheme["status"]=="Error"){
		return temp_scheme;
	}
	$dat_scheme=$temp_scheme["message"];
	$tables=$dat_scheme["tables_names"];
	$fields_tables=$dat_scheme["fields_tables"];
	
    if(set_foreign_check($conexion,$bd,false)==false){
		return ["status"=>"Error","message"=>"Imposible desactivar Foreign Check"];
	}
	for($i=0;$i<count($tables);$i++){
		if(array_key_exists($tables[$i],$data_tables)==false){
			mysqli_rollback($conexion);
			$msg="Falta Datos de las Tablas de la Base de Datos";
			if(set_foreign_check($conexion,$bd,true)==false){
				$msg=$msg.", Error Reactivando Foreign Check";
			}
			return ["status"=>"Error","message"=>$msg];
		}
		$res_tabl=get_fields($tables[$i]);
		if($res_tabl["status"]=="Error"){
			mysqli_rollback($conexion);
			$msg=$res["message"];
			if(set_foreign_check($conexion,$bd,true)==false){
				$msg=$msg.", Error Reactivando Foreign Check";
			}
			$res["message"]=$msg;
		    return $res;
		}
		$expected_fields=$res_tabl["message"];
		$tabl_target=$tables[$i];
		if(reset_table($conexion,$bd,$tabl_target)==false){
			mysqli_rollback($conexion);
			$msg="Imposible Truncar Tabla {$tabl_target}";
			if(set_foreign_check($conexion,$bd,true)==false){
				$msg=$msg.", Error Reactivando Foreign Check";
			}
		    return ["status"=>"Error","message"=>$msg];
		}
		$dat_tabl_target=$data_tables[$tabl_target];
		$list_rows=array();
		for($j=0;$j<count($dat_tabl_target);$j++){
			$next_row=$dat_tabl_target[$j];
			foreach ($next_row as $key=>$value){
				$exist_field=false;
				for($k=0;$k<count($expected_fields);$k++){
					if($expected_fields[$k]==$key){
						$exist_field=true;
						$k=count($expected_fields);
					}
				}
			    if($exist_field==false){
				   mysqli_rollback($conexion);
				   $msg="Campos Enviados Invalido";
				   if(set_foreign_check($conexion,$bd,true)==false){
				       $msg=$msg.", Error Reactivando Foreign Check";
			       }
		           return ["status"=>"Error","message"=>$msg,"expected"=>$expected_fields,"getted"=>$next_row];
			    }
				$list_rows[$j][$key]=$value;
		    }
		}
		for($j=0;$j<count($list_rows);$j++){
			add_data($conexion,$bd,$tabl_target,$list_rows[$j],true);
		}
	}
	mysqli_commit($conexion);
	if(set_foreign_check($conexion,$bd,true)==false){
	    return ["status"=>"Error","message"=>"Restauracion Realizada pero no se pudo Reactivar Foreign Check"];
	}
	$primary_fields=get_primary_fields($dat_scheme);
	$seed_data=$dat_scheme["seed_data"];
	$res_seed=set_seed_data($conexion,$bd,$seed_data,$primary_fields);
	if($res_seed["status"]=="Error"){
		return $res_seed;
	}
	return ["status"=>"Suceess","message"=>"Restauracion de La Base de Datos Realizada Exitosamente"];
	
}

//Respaldthe Data Base
function respald_bd($conexion,$bd){
	mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
	$temp_scheme=get_scheme_dat();
	if($temp_scheme["status"]=="Error"){
		return temp_scheme;
	}
	$dat_scheme=$temp_scheme["message"];
	$tables=$dat_scheme["tables_names"];
	$fields_tables=$dat_scheme["fields_tables"];
	$dat_tables=array();
	for($i=0;$i<count($tables);$i++){
		$dat_target=get_data($conexion,$bd,$tables[$i],array(),null,null,true);
		if($dat_target["status"]=="Error"){
			return $dat_target;
		}
		$dat_tables[$tables[$i]]=$dat_target["message"];
	}
	return ["status"=>"Suceess","message"=>"Respaldo Realizado Exitosamente","data"=>$dat_tables];
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