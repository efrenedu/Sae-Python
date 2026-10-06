<?php

//verify Integrity of Data Received
require_once __DIR__."/../../private/instituto/db_config.php";
require_once __DIR__."/../../private/instituto/jwt.php";
if(count($_POST)<6){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;	
}
if(!isset($_POST["user_register"]) || !isset($_POST["timestamp"]) || !isset($_POST["token_user"]) || !isset($_POST["preguntas_secretas"]) || !isset($_POST["password_register"]) || !isset($_POST["ci_worker"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;
}

date_default_timezone_set("America/Caracas");
$user_register=$_POST["user_register"];
$token_client=$_POST["token_user"];
$client_timestamp=$_POST["timestamp"];
$password_register=$_POST["password_register"];
$secrets_questions_list=json_decode($_POST["preguntas_secretas"],true);
$ci_worker=$_POST["ci_worker"];
$fecha_str=strval(date("d/m/Y"));

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
      echo json_encode(["status"=>"Error","message"=>"Debe ser el Administrador para Realizar El Registro de un Usuario"]);
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
date_default_timezone_set("America/Caracas");
$res=array();
$exist_user=id_exist($conexion,$db,"usuario","usuario",$user_register);
$exist_worker=id_exist($conexion,$db,"usuario","CI_trabaj",$ci_worker);
if($exist_user["status"]=="Error"){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode($exist_user);
   exit;
}
if($exist_worker["status"]=="Error"){
  http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode($exist_worker);
   exit;		
}
$err_msg_user="";
if($exist_user["message"]=="True"){
	$err_msg_user="El Usuario ya Existe";
}
else if($exist_worker["message"]=="True"){
   $err_msg_user="El Trabajador ya tiene un Usuario Asignado";
}
if($err_msg_user!=""){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>$err_msg_user]);
   exit;
}
$cond_data=array("conditions_Names"=>array("CI_trabaj"),"conditions_Values"=>array($ci_worker),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
$join_data=array();
$join_data["cargo"]=array("query_field"=>array("cargo"),"share_fields"=>array("field"=>"id_cargo","table_reference"=>"trabajador"),"Conditions_join"=>null);
	
$cargo_worker_res=get_data($conexion,$db,"trabajador",array(),$cond_data,$join_data,true);
if($cargo_worker_res["status"]=="Error"){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode($cargo_worker_res);
   exit;
	
}
$dat_worker=$cargo_worker_res["message"];
if(count($dat_worker)<=0){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Imposible Acceder al Cargo del Trabajador"]);
   exit;
}
$cargo=$dat_worker[0]["cargo"];
$access="";
$sub_dir_len=strlen("Sub Director");
$coordinador_len=strlen("Coordinador");
if($cargo=="Secretaria"){
	$access="secretaria";
}
else if(substr($cargo,0,$sub_dir_len)=="Sub Director"){
	$access="directivo";
}
else if(substr($cargo,0,$coordinador_len)=="Coordinador"){
	$access="coordinador";
}
if($access==""){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Imposible Asignar Nivel de Acceso al Usuario"]);
   exit;
}
$password_hash=password_hash($password_register,PASSWORD_BCRYPT);
$id_intentos="IntentosUser_{$user_register}";	
$dat_intentos=array("id_intentos"=>$id_intentos,"num_intentos"=>"0","last_fecha"=>"","last_hora"=>"","modificado"=>$fecha_str);
$register_res=add_data($conexion,$db,"intentos_usuario",$dat_intentos,true);
if($register_res["status"]=="Error"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode($register_res);
	exit;
}


$dat_user=array("usuario"=>$user_register,"password"=>$password_hash,"id_intentos"=>$dat_intentos["id_intentos"],"CI_trabaj"=>$ci_worker,"nivel_acceso"=>$access,"bloqueado"=>"False","foto"=>"fotos/user_login.jpg","modificado"=>$fecha_str);
$register_res=add_data($conexion,$db,"usuario",$dat_user,true);
if($register_res["status"]=="Error"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode($register_res);
	exit;
}

foreach($secrets_questions_list as $number_Question=>$dat_Question){
	$join_data=array();
	$question=$dat_Question["pregunta"];
	$answer=$dat_Question["respuesta"];
	$id_preg="SecretQuestion_{$user_register}_Question {$number_Question}";
	$dat_preg=array("id_pregunta"=>$id_preg,"pregunta"=>$question,"respuesta"=>$answer,"usuario"=>$user_register,"numero"=>$number_Question,"modificado"=>$fecha_str);
	$res_add=add_data($conexion,$db,"pregunta_secreta",$dat_preg,true);
	if($res_add["status"]=="Error"){
		http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
        echo json_encode($res_add);
	    exit;
	}
}

//Make Report
$hora_str=strval(date("H:i:s"));
$id_report="report_{$user_client}_{$fecha_str}{$hora_str}";
$data_report=array("id_reporte"=>$id_report,"usuario"=>$user_client,"fecha"=>$fecha_str,"hora"=>$hora_str,"tipo"=>"Actualizacion de Usuario","razon"=>"Cambio de Configuracion del Usuario","motivo"=>"","modificado"=>$fecha_str);
$res_add=add_data($conexion,$db,"reporte",$data_report,true,true);
if($res_add["status"]!="Error"){
	$res["status"]="Success";
	$res["message"]="Registro Realizo Existosamente";
}
else{
	$res=$res_add;
}



http_response_code(400);
header("Content-Type:application/json;charset=utf-8");
echo json_encode($res);


?>