<?php

function generate_password($size_pass=12){
	$new_pass="";
	$specials="!@#$%&*";
	$numbers="23456789";
	$characters="abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ";
	$max_len=strlen($characters)-1;
	for($i=0;$i<$size_pass-2;$i++){
		$new_pass.=$characters[random_int(0,$max_len)];
	}
	$new_pass.=$numbers[random_int(0,strlen($numbers)-1)];
	$new_pass.=$specials[random_int(0,strlen($specials)-1)];
	
	return $new_pass;
	
}
//verify Integrity of Data Received
require_once __DIR__."/../../private/instituto/db_config.php";
require_once __DIR__."/../../private/instituto/jwt.php";
if(count($_POST)<4){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;	
}
if(!isset($_POST["update_type"]) || !isset($_POST["timestamp"]) || !isset($_POST["token_user"]) || !isset($_POST["extra_data"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;
}
$update_type=$_POST["update_type"];
$token_client=$_POST["token_user"];
$client_timestamp=$_POST["timestamp"];
$extra_data=json_decode($_POST["extra_data"],true);

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
date_default_timezone_set("America/Caracas");
$res=array();
$msg_send="";
if(array_key_exists("user_modify",$extra_data)==false){
    http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Usuario Modificar no Recibido"]);
	exit;
}
$user_modify=$extra_data["user_modify"];
if($user_client==$user_modify){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"No puede Modificar al Usuario Administrador"]);
	exit;
	
}
if($update_type=="Delete User"){
	$cond_data=array("conditions_Names"=>array("usuario"),"conditions_Values"=>array($user_modify),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
	$res_delete=delete_data($conexion,$db,"pregunta_secreta",$cond_data,null);
	if($res_delete["status"]=="Error"){
         http_response_code(400);
         header("Content-Type:application/json;charset=utf-8");
         echo json_encode($res_delete);
	     exit;
	}
    $res_delete=delete_data($conexion,$db,"reporte",$cond_data,null);
	if($res_delete["status"]=="Error"){
         http_response_code(400);
         header("Content-Type:application/json;charset=utf-8");
         echo json_encode($res_delete);
	     exit;
	}
    $join_data=array();
	$join_data["intentos_usuario"]=array("query_field"=>array(),"share_fields"=>array("field"=>"id_intentos","table_reference"=>"usuario"),"Conditions_join"=>null);
	$cond_data=array("conditions_Names"=>array("usuario","nivel_acceso"),"conditions_Values"=>array($user_modify,"admin"),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","!="));
	$res_delete=delete_data($conexion,$db,"usuario",$cond_data,$join_data);
	if($res_delete["status"]=="Error"){
         http_response_code(400);
         header("Content-Type:application/json;charset=utf-8");
         echo json_encode($res_delete);
	     exit;
	}    
}
else if($update_type=="Reset Password"){
	$rand_pass=generate_password();
	$next_pass=password_hash($rand_pass,PASSWORD_BCRYPT);
	$cond_data=array("conditions_Names"=>array("usuario","nivel_acceso"),"conditions_Values"=>array($user_modify,"admin"),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","!="));
	$res_update=update_data($conexion,$db,"usuario",array("password"=>$next_pass),$cond_data,null);
	if($res_update["status"]=="Error"){
         http_response_code(400);
         header("Content-Type:application/json;charset=utf-8");
         echo json_encode($res_update);
	     exit;
	}   
    $msg_send=$rand_pass;	
}
else if($update_type=="Change_Access"){
	if(array_key_exists("access_requerid",$extra_data)==false){
		   http_response_code(400);
           header("Content-Type:application/json;charset=utf-8");
           echo json_encode(["status"=>"Error","message"=>"Nivel de Acceso a Modificar no Recibido"]);
	       exit;
    }
	$next_access=$extra_data["access_requerid"];
	if($next_access=="admin"){
		 http_response_code(400);
         header("Content-Type:application/json;charset=utf-8");
         echo json_encode(["status"=>"Error","message"=>"No se Puede Cambiar el Permiso de Un Usuario a Administrador"]);
	     exit;
	}
	$cond_data=array("conditions_Names"=>array("usuario","nivel_acceso"),"conditions_Values"=>array($user_modify,"admin"),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","!="));
	$res_update=update_data($conexion,$db,"usuario",array("nivel_acceso"=>$next_access),$cond_data,null);
	if($res_update["status"]=="Error"){
         http_response_code(400);
         header("Content-Type:application/json;charset=utf-8");
         echo json_encode($res_update);
	     exit;
	}		
}
else if($update_type=="Desbloquear"){
	$join_data=array();
    $join_data["intentos_usuario"]=array("query_field"=>array("num_intentos"=>"0","last_hora"=>"","last_fecha"=>""),"share_fields"=>array("field"=>"id_intentos","table_reference"=>"usuario"),"Conditions_join"=>null);
		 
	$cond_data=array("conditions_Names"=>array("usuario","nivel_acceso"),"conditions_Values"=>array($user_modify,"admin"),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","!="));
	$res_update=update_data($conexion,$db,"usuario",array("bloqueado"=>"False"),$cond_data,$join_data);
	if($res_update["status"]=="Error"){
         http_response_code(400);
         header("Content-Type:application/json;charset=utf-8");
         echo json_encode($res_update);
	     exit;
	}
}
	
//Make Report
$id_report=generate_id($conexion,$db,"reporte","id_reporte");
if($id_report["status"]=="Error"){
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode($id_report);
    exit;
}
$fecha_str=strval(date("d/m/Y"));
$hora_str=strval(date("H:i:s"));
$data_report=array("id_reporte"=>$id_report["message"],"usuario"=>$user_client,"fecha"=>$fecha_str,"hora"=>$hora_str,"tipo"=>"Actualizacion de Usuario","razon"=>"Cambio de Configuracion del Usuario","motivo"=>"","modificado"=>$fecha_str);
$res_add=add_data($conexion,$db,"reporte",$data_report,true,true);
if($res_add["status"]!="Error"){
	$res["status"]="Success";
	if($msg_send!=""){
		$res["message"]=$msg_send;
	}
	else{
	    $res["message"]="Modificaciones Realizadas Existosamente ";	
	}

}
else{
	$res=$res_add;
}



http_response_code(400);
header("Content-Type:application/json;charset=utf-8");
echo json_encode($res);


?>