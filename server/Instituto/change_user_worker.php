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
if(!isset($_POST["new_worker"]) || !isset($_POST["timestamp"]) || !isset($_POST["token_user"]) || !isset($_POST["old_worker"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;
}
$new_worker=$_POST["new_worker"];
$old_worker=$_POST["old_worker"];
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
if($user_access!="admin" && $user_access!="directivo"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Acceso Denegado solo el Administrador y Directivos pueden Modificar Trabajadores"]);
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

$conexion=$data_conexion["conector"];
$db=$data_conexion["db"];
date_default_timezone_set("America/Caracas");

$cond_data=array("conditions_Names"=>array("CI_trabaj"),"conditions_Values"=>array($old_worker),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
$old_dat_user=get_data($conexion,$db,"usuario",["usuario"],$cond_data,null,true);
if($old_dat_user["status"]=="Error"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode($id_dat);
	exit;
}
$old_dat_user=$old_dat_user["message"];
if(count($old_dat_user)<=0){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Success","message"=>"Trabajador sin Usuario"]);
	exit;
}

$id_dat=id_exist($conexion,$db,"trabajador","CI_trabaj",$new_worker);
if($id_dat["status"]=="Error"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode($id_dat);
	exit;
}
$id_dat=$id_dat["message"];
if($id_dat=="False"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Trabajador a Cambiar en el Usuario Inexistente"]);
	exit;
}

$cond_data=array("conditions_Names"=>array("usuario"),"conditions_Values"=>array($old_dat_user[0]["usuario"]),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
$res_update=update_data($conexion,$db,"usuario",array("CI_trabaj"=>$new_worker),$cond_data,null,true);  
if($res_update["status"]=="Error"){
    http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode($res_update);
	exit;

}	

http_response_code(400);
header("Content-Type:application/json;charset=utf-8");
echo json_encode(["status"=>"Success","message"=>"Trabajador del Usuario Modificado Existosamente"]);



?>