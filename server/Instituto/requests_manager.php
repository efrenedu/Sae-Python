<?php
//verify Integrity of Data Received
require_once __DIR__."/../../private/instituto/db_config.php";
require_once __DIR__."/../../private/instituto/jwt.php";

#verify if the request try to access to a Prohibited Table Data
function verify_tablesAccess($list_tables){
	$prohibited_tables=array("usuario","intentos_usuario","preguntas_secretas");
	for($i=0;$i<count($list_tables);$i++){
		for($j=0;$j<count($prohibited_tables);$j++){
		    if($list_tables[$i]==$prohibited_tables[$j]){
				return false;
			}
	    }
	}
	return true;
}

if(count($_POST)<4){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;	
}
if(!isset($_POST["request_type"]) || !isset($_POST["data_request"]) || !isset($_POST["timestamp"]) || !isset($_POST["token"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;
}

$path_secret_key=__DIR__."/../../private/instituto/secretToken.json";
if(!file_exists($path_secret_key)){
    http_response_code(500);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Error Obteniendo data de Configuracion del Token del Servidor"]);
    exit;
}   
$data_secretKey=json_decode(file_get_contents($path_secret_key),true);

$token_user=$_POST["token"];
$request_type=$_POST["request_type"];

//Verify TimeStamp
$client_timestamp=$_POST["timestamp"];
$timestamp_server=time();
$max_dif=5;
$dif_time=abs($timestamp_server-(int)$client_timestamp);
if($dif_time>$max_dif){
	http_response_code(401);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"La peticion ha expirado","dif_segundos"=>$dif_time]);
    exit;	
}


//convert the Data Received to JSON Format if is Neccesary
$request_dat=$_POST["data_request"];
if($request_dat!=""){
	$request_dat=json_decode($request_dat,true);
}

//Verify if the Request is Init the DB 
if($request_type=="Verify_db"){
	$res=verify_db();
	http_response_code(400);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode($res);
    exit;   
} 

//get data Conexion for Manage the Data Request of Client
$data_conexion=get_conexion();
$res_conex=$data_conexion["response"];
if($res_conex==-1){
	   http_response_code(500);
	   header("Content-Type:application/json;charset=utf-8");
	   echo json_encode(["status"=>"Error","message"=>"Error Obteniendo Informacion de Configuracion"]);
       exit;
}
else if($res_conex==-2){
	   http_response_code(500);
	   header("Content-Type:application/json;charset=utf-8");
	   echo json_encode(["status"=>"Error","message"=>"Error Conectando con la Base de Datos"]);
       exit;
}
$conexion=$data_conexion["conector"];
$db=$data_conexion["db"];
	
	
//Verify type of Request	
if($request_type=="Security Copies"){
	$valid_token=validar_token($token_user,$data_secretKey["Token"]);
    if($valid_token["Valido"]=="False"){
	   http_response_code(400);
       header("Content-Type:application/json;charset=utf-8");
       echo json_encode(["status"=>"Error","message"=>"Acceso Denegado, el token del Usuario es Invalido"]);
       exit;
    }
	$payload_data=$valid_token["Message"];
	if($payload_data["Acceso"]!="admin"){
	   http_response_code(400);
       header("Content-Type:application/json;charset=utf-8");
       echo json_encode(["status"=>"Error","message"=>"Acceso Denegado,el Usuario No tiene permisos para la Accion"]);
       exit;
	}
	$id_request=$request_dat["Action"];
	$res=array();
	if($id_request=="Restore"){
		if(count($_FILES)<=0){
			 http_response_code(400);
             header("Content-Type:application/json;charset=utf-8");
             echo json_encode(["status"=>"Error","message"=>"Faltan Datos"]);
             exit;
	
		}
		
		if(!isset($_FILES["source"])){
			 http_response_code(400);
             header("Content-Type:application/json;charset=utf-8");
             echo json_encode(["status"=>"Error","message"=>"Datos Invalidos"]);
             exit;
		}
		copy($_FILES["source"]["tmp_name"],$_FILES["source"]["name"]);
        $nombre=$_FILES["source"]["name"];
	    $posibles=array(".zip",".rar");
	    $valid_format=false;
	    foreach($posibles as $posible_target){
		    $size=strlen($posible_target);
	        if(substr($nombre,-$size,$size)==$posible_target){
		       $valid_format=true;
		       break;
	        }
	    }
	    if($valid_format==false){
  	        if(file_exists(__DIR__.DIRECTORY_SEPARATOR.$nombre)){
		        unlink(__DIR__.DIRECTORY_SEPARATOR.$nombre);
	        }
			http_response_code(400);
            header("Content-Type:application/json;charset=utf-8");
            echo json_encode(["status"=>"Error","message"=>"Invalid File Format, Upload ZIP "]);
	        exit;
	    }
	    $dir="respaldos".DIRECTORY_SEPARATOR.$nombre;
        move_uploaded_file($_FILES["source"]["tmp_name"],$dir);
	    if(file_exists(__DIR__.DIRECTORY_SEPARATOR.$nombre)){
		    unlink(__DIR__.DIRECTORY_SEPARATOR.$nombre);
	    }
		$zip=new ZipArchive();
	    $zip_server_name=$dir;
	    $nombre_zip=__DIR__.DIRECTORY_SEPARATOR.$dir;
	    $ruta_files=__DIR__.DIRECTORY_SEPARATOR."respaldos";
	    $files_contains=array();
	    if($zip->open($nombre_zip)){
		    $zip->extractTo($ruta_files);
		    $zip->close();
		    $error=false;
		    $archivos=new RecursiveIteratorIterator(new RecursiveDirectoryIterator(__DIR__.DIRECTORY_SEPARATOR."respaldos"),RecursiveIteratorIterator::LEAVES_ONLY);
		    $abs_paths=array();
		    $tables_names=array();
		    foreach ($archivos as $f){
			    if($f->isDir()){
				    continue;
			    }
			    $ruta_abs=$f->getRealPath();
			    $nombre_file=basename($ruta_abs);
			    $size_csv=strlen(".csv");
	            if(substr($nombre_file,-$size_csv,$size_csv)==".csv"){
		           $abs_paths[]=$ruta_abs;
				   $next_tabl=explode(".csv",$nombre_file)[0];
				   if($next_tabl=="anos_incorporados"){
					   $next_tabl="años_incorporados";
				   }
			       $tables_names[]=$next_tabl;
	           }
		    }
			if(count($abs_paths)<=0){
				if(file_exists($nombre_zip)){
			        unlink($nombre_zip);
			    }
				http_response_code(400);
                header("Content-Type:application/json;charset=utf-8");
	            echo json_encode(["status"=>"Error","message"=>"No Existen Archivos dentro del Backup"]);
                exit;
			}
			
		    ini_set('output_buffering','off');
	        ini_set('zlib.output_compression',false);
	        ob_implicit_flush(true);
    	    while(ob_get_level()) ob_end_flush();
		    header("Content-Type:application/x-ndjson;charset=utf-8");
		    foreach(restore_bd($conexion,$db,$abs_paths,$tables_names) as $estado){
			    echo json_encode($estado,JSON_UNESCAPED_UNICODE)."\n";
			    flush();
		    }
			$abs_paths[]=$nombre_zip;
		    foreach ($abs_paths as $target_path){
			    if(file_exists($target_path)){
				    unlink($target_path);
			    }
	        } 
		     
		    exit;
		}
		else{
		    if(file_exists($nombre_zip)){
			    unlink($nombre_zip);
			}
			http_response_code(400);
            header("Content-Type:application/json;charset=utf-8");
	        echo json_encode(["status"=>"Error","message"=>"imposible leer el Archivo Zip"]);
            exit;
		}
	}
	else{
		$base_path=__DIR__.DIRECTORY_SEPARATOR;
		$res=respald_bd($conexion,$db,$base_path);
		http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
	    echo json_encode($res);
        exit;
	}
	 
}
else if($request_type=="Id Manager"){
	$field_verify=$request_dat["field_required"];
	$tabl_target=$request_dat["target_table"];
	$id_request=$request_dat["Id_Request"];
	$res=array();
	if($id_request=="Generate Id"){
		$res=generate_id ($conexion,$db,$tabl_target,$field_verify);
	}
	else{
		//Id Exist Request
		$valid_token=validar_token($token_user,$data_secretKey["Token"]);
        if($valid_token["Valido"]=="False"){
	        http_response_code(400);
            header("Content-Type:application/json;charset=utf-8");
            echo json_encode(["status"=>"Error","message"=>$valid_token["Message"]]);
            exit;
        }
		$field_value=$request_dat["field_Value"];
		$res=id_exist($conexion,$db,$tabl_target,$field_verify,$field_value);
	}
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
	echo json_encode($res);
    exit;   
}
else if($request_type=="Is_Empty"){
	    $tabl=$request_dat["target_table"];
	    $res=is_empty($conexion,$db,$tabl);
		http_response_code(400);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode($res);
        exit;  
}
else if($request_type=="Get Data"){
	    $join_dat=$request_dat["join_dat"];
		$tabl=$request_dat["target_table"];
		$tables_list=array($tabl);
		if($join_dat!=null){
			foreach($join_dat as $tabl_join=>$dat_join){
				$tables_list[]=$tabl_join;
			}
		}
		
		if(verify_tablesAccess($tables_list)==false){
			http_response_code(400);			
            header("Content-Type:application/json;charset=utf-8");
			echo json_encode(["status"=>"Error","message"=>"Acceso Denegado, No se Puede Hacer Consultas hacia las Tablas Solicitadas"]);
            exit;
		}
		$fields=$request_dat["fields"];
		$cond_dat=$request_dat["cond_dat"];
		$as_dict=$request_dat["as_dict"];
	    $res=get_data($conexion,$db,$tabl,$fields,$cond_dat,$join_dat,$as_dict);
		http_response_code(400);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode($res);
        exit;   
		
}
else{
	#Request to Multi Modifications
	$list_query=$request_dat["query_list"];
	if(array_key_exists("query_list",$request_dat)==false){
		http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
        echo json_encode(["status"=>"Error","message"=>"Datos de Peticiones No Recibidos"]);
        exit;
	}
	$token_verified=false;
	foreach ($list_query as $query_target){
		$query_type=$query_target["Type"];
		$query_values=$query_target["Values"];
		$query_table=$query_target["Table"];
		$query_conds=$query_target["Conditions"];
		$query_joins=$query_target["Join"];
		$list_tables=array($query_table);
		if($query_joins!=null){
		  foreach($query_joins as $tabl_join=>$dat_join){
			  $list_tables[]=$tabl_join;
		  }
		}
		if(verify_tablesAccess($list_tables)==false){
			http_response_code(400);
            header("Content-Type:application/json;charset=utf-8");
            echo json_encode(["status"=>"Error","message"=>"Acceso Denegado, No se Puede Hacer Consultas hacia las Tablas Solicitadas"]);
            exit;
		}
		
		if($token_verified==false){
			$require_verify_token=true;
			if($query_type=="Add"){
			    if($query_table=="descarga_documentos" || $query_table=="reporte"){
			        $require_verify_token=false;
		       }
		   }
		   if($require_verify_token==true){
			    $token_verified=true;
			    $valid_token=validar_token($token_user,$data_secretKey["Token"]);
                if($valid_token["Valido"]=="False"){
	               http_response_code(400);
                   header("Content-Type:application/json;charset=utf-8");
                   echo json_encode(["status"=>"Error","message"=>$valid_token["Message"]]);
                   exit;
               }
		   }
		}
		$res=array();
		if($query_type=="Add"){
			 $from_dict=false;
			 if(array_key_exists("from_dict",$query_target)==true){
				 $from_dict=$query_target["from_dict"];
			 }
             $res=add_data($conexion,$db,$query_table,$query_values,$from_dict,false);
	    }
		else if($query_type=="Update"){
			 $res=update_data($conexion,$db,$query_table,$query_values,$query_conds,$query_joins,false);
		}
		else if($query_type=="Delete"){
			 
			 $res=delete_data($conexion,$db,$query_table,$query_conds,$query_joins,false);
		}
		if($res["status"]=="Error"){
			http_response_code(400);
	        header("Content-Type:application/json;charset=utf-8");
	        echo json_encode($res);
            exit;
		}	
	}
	finish_commit($conexion);
	http_response_code(400);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Success","message"=>"Peticiones Ejecutadas Exitosamente"]);
    exit;

}

?>
