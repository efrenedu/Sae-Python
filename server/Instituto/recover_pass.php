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
if(!isset($_POST["fase"]) || !isset($_POST["timestamp"]) || !isset($_POST["user_client"]) || !isset($_POST["extra_data"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;
}
$fase_actual=$_POST["fase"];
$user_client=$_POST["user_client"];
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
if($fase_actual=="Get User Data"){
  $join_data=array();
  $join_data["pregunta_secreta"]=array("query_field"=>array("pregunta"),"share_fields"=>array("field"=>"usuario","table_reference"=>"usuario"),"Conditions_join"=>null);
  $cond_data=array("conditions_Names"=>array("usuario","bloqueado"),"conditions_Values"=>array($user_client,"False"),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","="));
  $res=get_data($conexion,$db,"usuario",array("usuario"),$cond_data,$join_data,true);  
  if($res["status"]!="Error"){
	  $dat=$res["message"];
	  $preguntas=array();
	  for($i=0;$i<count($dat);$i++){
		  $preguntas[]=$dat[$i]["pregunta"];
	  } 
	  if(count($preguntas)<=0){
		  http_response_code(400);
          header("Content-Type:application/json;charset=utf-8");
          echo json_encode(["status"=>"Error","message"=>"Usuario Inexistente o Bloqueado"]);
	      exit;
	  }
	  $val_rand=rand(0,count($preguntas)-1);
	  $res["message"]=$preguntas[$val_rand];
	  
  }
}
else if($fase_actual=="Verify Secret Question"){
	if((array_key_exists("pregunta",$extra_data))==false || (array_key_exists("respuesta",$extra_data))==false){
		http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
        echo json_encode(["status"=>"Error","message"=>"Datos de Preguntas Secretas no Recibidos"]);
	    exit;
	}
	$pregunta=$extra_data["pregunta"];
	$respuesta=$extra_data["respuesta"];
	$join_data=array();
	$conditions_join=array("conditions_Names"=>array("pregunta","respuesta"),"conditions_Values"=>array($pregunta,$respuesta),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","="));
    $join_data["pregunta_secreta"]=array("query_field"=>array(),"share_fields"=>array("field"=>"usuario","table_reference"=>"usuario"),"Conditions_join"=>$conditions_join);
    $cond_data=array("conditions_Names"=>array("usuario","bloqueado"),"conditions_Values"=>array($user_client,"False"),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","="));
    $res=get_data($conexion,$db,"usuario",array("nivel_acceso","CI_trabaj","usuario"),$cond_data,$join_data,true);  
    if($res["status"]!="Error"){
	     if(count($res["message"])<=0){
			 http_response_code(400);
             header("Content-Type:application/json;charset=utf-8");
             echo json_encode(["status"=>"Error","message"=>"Las Respuesta No Coincide con la Pregunta"]);
	         exit;
		 }
		 $data_user=$res["message"][0];
		 $datos_session=["CI_trabaj"=>$data_user["CI_trabaj"],"Nivel_Acceso"=>$data_user["nivel_acceso"],"Id_User"=>$data_user["usuario"]];
	     $path_keySecret=__DIR__."/../../private/instituto/secretToken_recoverPass.json";
         if(!file_exists($path_keySecret)){
	        http_response_code(500);
	        header("Content-Type:application/json;charset=utf-8");
	        echo json_encode(["status"=>"Error","message"=>"Error Inesperado, Archivos Faltantes para generar Token"]);
            exit;
         }
         $data_secretKey=json_decode(file_get_contents($path_keySecret),true);
		 $token_temp=generate_tokenLogin($datos_session,$data_secretKey["Token"],300);
         $res["message"]=$token_temp;
	}
}
else if($fase_actual=="Update Password"){
	if((array_key_exists("password_request",$extra_data))==false || (array_key_exists("token",$extra_data))==false){
		http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
        echo json_encode(["status"=>"Error","message"=>"Datos de Preguntas Secretas no Recibidos"]);
	    exit;
	}
	$token=$extra_data["token"];
	$password_request=$extra_data["password_request"];
    $path_keySecret=__DIR__."/../../private/instituto/secretToken_recoverPass.json";
    if(!file_exists($path_keySecret)){
	    http_response_code(500);
        header("Content-Type:application/json;charset=utf-8");
	    echo json_encode(["status"=>"Error","message"=>"Error Inesperado, Archivos Faltantes para generar Token"]);
        exit;
    }
    $data_secretKey=json_decode(file_get_contents($path_keySecret),true);
	$res_token=validar_token($token,$data_secretKey["Token"]);
    if($res_token["Valido"]=="False"){
		http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
        echo json_encode(["status"=>"Error","message"=>$res_token["Message"]]);
	    exit;
	}
	$user_modify=$res_token["Message"]["Id_usr"];
    $next_pass=password_hash($password_request,PASSWORD_BCRYPT);
    $cond_dat=array("conditions_Names"=>array("usuario"),"conditions_Values"=>array($user_client),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
	$res_update=update_data($conexion,$db,"usuario",array("password"=>$next_pass),$cond_dat,null,true);
	if($res_update["status"]=="Error"){
		http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
        echo json_encode(["status"=>"Error","message"=>$res_update]);
	    exit; 
	}
	$res=["status"=>"Success","message"=>"Contraseña Modificada Exitosamente"];
}
http_response_code(400);
header("Content-Type:application/json;charset=utf-8");
echo json_encode($res);


?>