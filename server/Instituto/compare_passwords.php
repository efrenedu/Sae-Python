<?php
require_once __DIR__."/../../private/instituto/db_config.php";
require_once __DIR__."/../../private/instituto/jwt.php";
if(count($_POST)<4){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;	
}
if(!isset($_POST["timestamp"]) || !isset($_POST["token"]) || !isset($_POST["password_send"]) || !isset($_POST["user_verify"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;
}
$token_client=$_POST["token"];
$client_timestamp=$_POST["timestamp"];
$user_verify=$_POST["user_verify"];
$passw_received=$_POST["password_send"];


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

$path_secret_key=__DIR__."/../../private/instituto/secretToken.json";
if(!file_exists($path_secret_key)){
    http_response_code(500);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Error Obteniendo data de Configuracion del Token del Servidor"]);
    exit;
}   

$data_secretKey=json_decode(file_get_contents($path_secret_key),true);
$valid_token=validar_token($token_client,$data_secretKey["Token"]);
//Verify the Token of User if is Invalid send the Login/Inicio Panel Data
if($valid_token["Valido"]=="False"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Acceso Denegado, el token del Usuario es Invalido"]);
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
$query="";
if($user_verify=="Admin_User"){
	$user_verify="admin";
	$query="SELECT password FROM ".$db.".usuario WHERE nivel_acceso=?";
}
else{
	$query="SELECT password FROM ".$db.".usuario WHERE usuario=?";
}
$statment=mysqli_prepare($conexion,$query);
if(!$statment){
	http_response_code(500);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"Error Preparando Consulta"]);
    exit;
}
mysqli_stmt_bind_param($statment,"s",$user_verify);
if(!mysqli_stmt_execute($statment)){
	http_response_code(500);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"Error Preparando Consulta"]);
    exit;
}

$res=$statment->get_result();
$dict_res=$res->fetch_assoc();
$statment->close();
if($dict_res==null){
	http_response_code(400);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"Usuario Solicitado Inexistente"]);
    exit;
}
$password_required=$dict_res["password"];
$msg="Different Password";
if(password_verify($passw_received,$password_required)){
	$msg="Same Password";
}
http_response_code(400);
header("Content-Type:application/json;charset=utf-8");
echo json_encode(["status"=>"Success","message"=>$msg]);


?>