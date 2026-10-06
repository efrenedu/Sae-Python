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
$list_updates=array();
if($update_type!=""){
    $list_updates=explode(";",$update_type);
}
//Update Everything Except for Secret_Questions
foreach($list_updates as $update_target){
	if($update_target=="Image Icon"){
       if(array_key_exists("image_icon",$extra_data)==false){
		   http_response_code(400);
           header("Content-Type:application/json;charset=utf-8");
           echo json_encode(["status"=>"Error","message"=>"Imagen a Modificar no Recibido"]);
	       exit;
       }    
       $foto_value=$extra_data["image_icon"];
       $cond_data=array("conditions_Names"=>array("usuario"),"conditions_Values"=>array($user_client),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
       $res_update=update_data($conexion,$db,"usuario",array("foto"=>$foto_value),$cond_data,null);  
       if($res_update["status"]=="Error"){
	        http_response_code(400);
            header("Content-Type:application/json;charset=utf-8");
            echo json_encode($res_update);
	        exit; 
       }
   }
   else if($update_target=="Password"){
	   if(array_key_exists("password_requerid",$extra_data)==false){
		   http_response_code(400);
           header("Content-Type:application/json;charset=utf-8");
           echo json_encode(["status"=>"Error","message"=>"Password a Modificar no Recibido"]);
	       exit;
	   }
	   $password_requerid=$extra_data["password_requerid"];
	   $next_pass=password_hash($password_requerid,PASSWORD_BCRYPT);
       $cond_data=array("conditions_Names"=>array("usuario"),"conditions_Values"=>array($user_client),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
       $res_update=update_data($conexion,$db,"usuario",array("password"=>$next_pass),$cond_data,null);  
       if($res_update["status"]=="Error"){
	        http_response_code(400);
            header("Content-Type:application/json;charset=utf-8");
            echo json_encode($res_update);
	        exit; 
       }   
   }
   else if($update_target=="Change_Worker_Admin"){
	   if($user_access!="admin"){
		    http_response_code(400);
            header("Content-Type:application/json;charset=utf-8");
            echo json_encode(["status"=>"Error","message"=>"Acceso Denegado, No tiene Permiso para Modificar el Trabajador del Administrador"]);
	        exit; 
		   
	   }
	   if(array_key_exists("ci_worker",$extra_data)==false){
		   http_response_code(400);
           header("Content-Type:application/json;charset=utf-8");
           echo json_encode(["status"=>"Error","message"=>"Trabajdor CI a Modificar no Recibido"]);
	       exit;
	   }
	   $ci_requerid=$extra_data["ci_worker"];
	   $id_dat=id_exist($conexion,$db,"trabajador","CI_trabaj",$ci_requerid);
       if($id_dat["status"]=="Error"){
		   http_response_code(400);
           header("Content-Type:application/json;charset=utf-8");
           echo json_encode($id_dat);
	       exit;
	   }
	   $cond_data=array("conditions_Names"=>array("CI_trabaj"),"conditions_Values"=>array($ci_requerid),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));		 
	   $users_worker=get_data($conexion,$db,"usuario",array("nivel_acceso"),$cond_data,null,true);
	   if($users_worker["status"]=="Error"){
		   http_response_code(400);
           header("Content-Type:application/json;charset=utf-8");
           echo json_encode($users_worker);
	       exit;
	   }
	   $users_worker=$users_worker["message"];
	   if(count($users_worker)>0){
		   $temp_user=$users_worker[0];
		   if($temp_user["nivel_acceso"]!="admin"){
			  http_response_code(400);
              header("Content-Type:application/json;charset=utf-8");
              echo json_encode(["status"=>"Error","message"=>"No se puede Asignar Usuario Administrador a un Trabajador con Usuario Asignado,Por Favor Elimine Primero el Usuario Asignado en la Gestion de Usuarios antes de Designarlo como Administrador"] );
	          exit;   
		   }
		   else{
			   $ci_requerid="";
		   }
	   }
	   
	   if($id_dat["message"]=="True" && $ci_requerid!=""){
		  $cond_old_worker=array("conditions_Names"=>array("usuario","nivel_acceso"),"conditions_Values"=>array($user_client,"admin"),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","="));
		  $old_worker_dat=get_data($conexion,$db,"usuario",array("CI_trabaj"),$cond_old_worker,null,true);	
		  if($old_worker_dat["status"]=="Error"){
			  http_response_code(400);
              header("Content-Type:application/json;charset=utf-8");
              echo json_encode($old_worker_dat);
	          exit;  
			  
		  }
		  $cond_data=array("conditions_Names"=>array("usuario","nivel_acceso"),"conditions_Values"=>array($user_client,"admin"),"condition_Types"=>array("and","and"),"conditions_Verify"=>array("=","="));
		  $res_update=update_data($conexion,$db,"usuario",array("CI_trabaj"=>$ci_requerid),$cond_data,null);
          if($res_update["status"]=="Error"){
			 http_response_code(400);
             header("Content-Type:application/json;charset=utf-8");
             echo json_encode($res_update);
	         exit;  
		  }
		
		  $join_data=array();
		  $cond_data=array("conditions_Names"=>array("CI_trabaj"),"conditions_Values"=>array($ci_requerid),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));		 
		  $join_data["cargo"]=array("query_field"=>array("cargo"=>"Director"),"share_fields"=>array("field"=>"id_cargo","table_reference"=>"trabajador"),"Conditions_join"=>null);
		  $res_update=update_data($conexion,$db,"trabajador",array(),$cond_data,$join_data);
          if($res_update["status"]=="Error"){
			 http_response_code(400);
             header("Content-Type:application/json;charset=utf-8");
             echo json_encode($res_update);
	         exit;  
		  }
		
		  if(count($old_worker_dat["message"])>0){
			  $ci_old_woerker=$old_worker_dat["message"][0]["CI_trabaj"];
			  $join_data_worker=array();
		      $cond_data_worker=array("conditions_Names"=>array("CI_trabaj"),"conditions_Values"=>array($ci_old_woerker),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
	          $join_data_worker["cargo"]=array("query_field"=>array("cargo"=>"Docente"),"share_fields"=>array("field"=>"id_cargo","table_reference"=>"trabajador"),"Conditions_join"=>null);
              $res_update_worker=update_data($conexion,$db,"trabajador",array(),$cond_data_worker,$join_data_worker);
              if($res_update_worker["status"]=="Error"){
			      http_response_code(400);
                  header("Content-Type:application/json;charset=utf-8");
                  echo json_encode($res_update_worker);
	               exit;  
		      }

		  }
		  
	   }
	   
   }
	
}

//Update Secret_Questions
if(array_key_exists("secret_questions",$extra_data)==false){
	http_response_code(400);
	var_dump($extra_data);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Datos de Preguntas Secretas no Recibidos"]);
	exit;
}
$secrets_questions_list=$extra_data["secret_questions"];
$cond_data=array("conditions_Names"=>array("usuario"),"conditions_Values"=>array($user_client),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
foreach($secrets_questions_list as $number_Question=>$dat_Question){
	$join_data=array();
	$question=$dat_Question["pregunta"];
	$answer=$dat_Question["respuesta"];
	$conditions_join=array("conditions_Names"=>array("numero"),"conditions_Values"=>array($number_Question),"condition_Types"=>array("and"),"conditions_Verify"=>array("="));
    $join_data["pregunta_secreta"]=array("query_field"=>array("pregunta"=>$question,"respuesta"=>$answer),"share_fields"=>array("field"=>"usuario","table_reference"=>"usuario"),"Conditions_join"=>$conditions_join);
    $res_update=update_data($conexion,$db,"usuario",array(),$cond_data,$join_data);
	if($res_update["status"]=="Error"){
		http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
        echo json_encode($res_update);
	     exit;
	}
}

//Make Report
$fecha_str=strval(date("d/m/Y"));
$hora_str=strval(date("H:i:s"));
$id_report="report_{$user_client}_{$fecha_str}{$hora_str}";
$data_report=array("id_reporte"=>$id_report,"usuario"=>$user_client,"fecha"=>$fecha_str,"hora"=>$hora_str,"tipo"=>"Actualizacion de Usuario","razon"=>"Cambio de Configuracion del Usuario","motivo"=>"","modificado"=>$fecha_str);
$res_add=add_data($conexion,$db,"reporte",$data_report,true,true);
if($res_add["status"]!="Error"){
	$res["status"]="Success";
	$res["message"]="Modificaciones Realizadas Existosamente";
}
else{
	$res=$res_add;
}



http_response_code(400);
header("Content-Type:application/json;charset=utf-8");
echo json_encode($res);


?>