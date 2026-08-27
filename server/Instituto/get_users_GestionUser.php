<?php

//verify Integrity of Data Received
require_once __DIR__."/../../private/instituto/db_config.php";
require_once __DIR__."/../../private/instituto/jwt.php";
if(count($_POST)<2){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;	
}
if( !isset($_POST["timestamp"]) || !isset($_POST["token_user"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;
}

$token_client=$_POST["token_user"];
$client_timestamp=$_POST["timestamp"];

//Verify TimeStamp
$timestamp_server=time();
$max_dif=5;
$dif_time=abs($timestamp_server-(int)$client_timestamp);
if($dif_time>$max_dif){
	http_response_code(401);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"La peticion ha expirado","dif_segundos"=>$dif_time]);
    exit;	
}

$path_keySecret=__DIR__."/../../private/instituto/secretToken.json";
if(!file_exists($path_keySecret)){
	http_response_code(500);
    header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"Error Inesperado, Archivos Faltantes para generar Token"]);
    exit;
}
$data_secretKey=json_decode(file_get_contents($path_keySecret),true);
$res_token=validar_token($token_client,$data_secretKey["Token"]);
if($res_token["Valido"]=="False"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>$res_token["Message"]]);
	exit;
}
	
$user_client=$res_token["Message"]["Id_usr"];
$user_access=$res_token["Message"]["Acceso"];
if($user_access!="admin"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Acceso Denegado, Solo el Administrador puede Acceder"]);
	exit;
}
//Try to get the Connection of DataBase
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

//Send the query of User Data
$conexion=$data_conexion["conector"];
$db=$data_conexion["db"];
$res=array();
$cond_data=array("conditions_Names"=>array("nivel_acceso"),"conditions_Values"=>array("admin"),"condition_Types"=>array("and"),"conditions_Verify"=>array("!="));
$join_data=array();
$join_data["intentos_usuario"]=array("query_field"=>array("num_intentos"),"share_fields"=>array("field"=>"id_intentos","table_reference"=>"usuario"),"Conditions_join"=>null);
$res=get_data($conexion,$db,"usuario",array("usuario","CI_trabaj","nivel_acceso","bloqueado"),$cond_data,$join_data,true);
http_response_code(400);
header("Content-Type:application/json;charset=utf-8");
echo json_encode($res);


?>