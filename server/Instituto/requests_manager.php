<?php
//verify Integrity of Data Received
require_once __DIR__."/../../private/instituto/db_config.php";
require_once __DIR__."/../../private/instituto/jwt.php";
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
		$dat_tables=$request_dat["data_tables"]; 
		$res=restore_bd($conexion,$db,$dat_tables);
	}
	else{
		$res=respald_bd($conexion,$db);
	}
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
	echo json_encode($res);
    exit; 
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
		$field_value=$request_dat["field_Value"];
		$res=id_exist($conexion,$db,$tabl_target,$field_verify,$field_value);
	}
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
	echo json_encode($res);
    exit;   
}
else{
	if($request_type=="Get Data"){
		$fields=$request_dat["fields"];
		$cond_dat=$request_dat["cond_dat"];
		$join_dat=$request_dat["join_dat"];
		$tabl=$request_dat["target_table"];
		$as_dict=$request_dat["as_dict"];
		$res=get_data($conexion,$db,$tabl,$fields,$cond_dat,$join_dat,$as_dict);
		http_response_code(400);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode($res);
        exit;   
		
	}
	else if($request_type=="Update Data"){
		$fields_dat=$request_dat["fields_update"];
		$cond_dat=$request_dat["cond_dat"];
		$join_dat=$request_dat["join_dat"];
		$tabl=$request_dat["target_table"];
		$do_commit=$request_dat["commit"];
		$res=update_data($conexion,$db,$tabl,$fields_dat,$cond_dat,$join_dat,$do_commit);
		http_response_code(400);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode($res);
        exit;   
	}
	else if($request_type=="Delete Data"){
		$cond_dat=$request_dat["cond_dat"];
		$join_dat=$request_dat["join_dat"];
		$tabl=$request_dat["target_table"];
		$do_commit=$request_dat["commit"];
		$res=delete_data($conexion,$db,$tabl,$cond_dat,$join_dat,$do_commit);
		http_response_code(400);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode($res);
        exit;   
	}
	else if($request_type=="Add Data"){
		$tabl=$request_dat["target_table"];
		$values_dat=$request_dat["values_add"];
		$from_dict=$request_dat["from_dict"];
		$do_commit=$request_dat["commit"];
		$res=add_data($conexion,$db,$tabl,$values_dat,$from_dict,$do_commit);
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
}
    http_response_code(400);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"Error desconocido"]);
    exit;  
?>
