<?php

//verify Integrity of Data Received
require_once __DIR__."/../../private/instituto/db_config.php";
require_once __DIR__."/../../private/instituto/jwt.php";
if(count($_POST)<3){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;	
}
if(!isset($_POST["password"]) || !isset($_POST["timestamp"]) || !isset($_POST["user_client"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes"]);
   exit;
}
$pass_client=$_POST["password"];
$user_client=$_POST["user_client"];
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
$query_join="INNER JOIN ".$db.".intentos_usuario ON ".$db.".intentos_usuario.id_intentos=".$db.".usuario.id_intentos ";
$query="SELECT password,foto,nivel_acceso,CI_trabaj,bloqueado,num_intentos,last_fecha,last_hora FROM ".$db.".usuario ".$query_join." WHERE usuario=?";
$statment=mysqli_prepare($conexion,$query);
if(!$statment){
	http_response_code(500);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"Error Preparando Consulta"]);
    exit;
}
mysqli_stmt_bind_param($statment,"s",$user_client);
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
	echo json_encode(["status"=>"Error","message"=>"Usuario Inexistente"]);
    exit;
}

$bloqueado=$dict_res["bloqueado"];
$num_intentos=(int)$dict_res["num_intentos"];
$last_fecha=$dict_res["last_fecha"];
$temp_fecha=explode("/",$last_fecha);
$last_loggin="";
$last_hora=$dict_res["last_hora"];
if(count($temp_fecha)>=3){
	$formatted_date=$temp_fecha[0]."-".$temp_fecha[1]."-".$temp_fecha[2];
    $last_loggin=$formatted_date." ".$last_hora;
}
date_default_timezone_set("America/Caracas");
$minutes_dif=0;
if($last_loggin!=""){
	$date_intento=new DateTime($last_loggin);
	$actual_date=new DateTime();
	$dif_time=$date_intento->diff($actual_date);
	$minutes_dif=($dif_time->days*24*60)+($dif_time->h*60)+$dif_time->i;
}
if($bloqueado=="True"){
	if($minutes_dif>60){
		$bloqueado="False";
		$num_intentos=0;
	}
}

//Verify the Password
$pass_bd=$dict_res["password"];
if(password_verify($pass_client,$pass_bd) && $bloqueado=="False"){
	//Loggin Succes
	$next_query="UPDATE ".$db.".usuario u JOIN ".$db.".intentos_usuario iu ON u.id_intentos=iu.id_intentos SET ";
	$next_query=$next_query."u.bloqueado=?,iu.num_intentos=?,iu.last_fecha=?,iu.last_hora=? WHERE u.usuario=?;";
	$next_intentos="0";
	$fecha_str="";
	$hora_str="";
	$statment=mysqli_prepare($conexion,$next_query);
    $error=true;
	if($statment!=null){
	   mysqli_stmt_bind_param($statment,"sssss",$bloqueado,$next_intentos,$fecha_str,$hora_str,$user_client);
	   if(mysqli_stmt_execute($statment)!=null){
		   $error=false;
		   mysqli_commit($conexion);
	   }
    }
    if($error==true){
	    http_response_code(500);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode(["status"=>"Error","message"=>"Error Inesperado al Actualizar Status del Usuario"]);
        exit;
    }
	$statment->close();
	$path_keySecret=__DIR__."/../../private/instituto/secretToken.json";
    if(!file_exists($path_keySecret)){
	    http_response_code(500);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode(["status"=>"Error","message"=>"Error Inesperado, Archivos Faltantes para generar Token"]);
        exit;
    }
    $data_secretKey=json_decode(file_get_contents($path_keySecret),true);
  
	$datos_session=["CI_trabaj"=>$dict_res["CI_trabaj"],"Nivel_Acceso"=>$dict_res["nivel_acceso"],"Id_User"=>$user_client];
	$dur_token=3600;
	$token_client=generate_tokenLogin($datos_session,$data_secretKey["Token"],$dur_token);
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Succes","Acces_User"=>$dict_res["nivel_acceso"],"Foto_User"=>$dict_res["foto"],"CI_trabaj"=>$dict_res["CI_trabaj"],"TokenSession"=>$token_client]);
}
else{
	
	//Loggin Fail, Update Intentos_usuario Data
	$fecha_str=strval(date("d/m/Y"));
    $hora_str=strval(date("H:i:s"));
	if($bloqueado=="True"){
		http_response_code(500);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode(["status"=>"Error","message"=>"Usuario Bloqueado"]);
        exit;
	}
	else{
		if($num_intentos>=0){
			if($minutes_dif>20){
				$num_intentos=0;
			}
			if($num_intentos<3){
		        $num_intentos+=1;
	        }
		}
		if($num_intentos>=3){
			$bloqueado="True";
		}
	}
	
	$next_query="UPDATE ".$db.".usuario u JOIN ".$db.".intentos_usuario iu ON u.id_intentos=iu.id_intentos SET ";
	$next_query=$next_query."u.bloqueado=?,iu.num_intentos=?,iu.last_fecha=?,iu.last_hora=? WHERE u.usuario=?;";
	
	$statment=mysqli_prepare($conexion,$next_query);
    $error=true;
	if($statment!=null){
	   $next_intentos=strval($num_intentos);
	   mysqli_stmt_bind_param($statment,"sssss",$bloqueado,$next_intentos,$fecha_str,$hora_str,$user_client);
	   if(mysqli_stmt_execute($statment)!=null){
		   $error=false;
		   mysqli_commit($conexion);
	   }
    }
	$statment->close();
    if($error==true){
	    http_response_code(500);
	    header("Content-Type:application/json;charset=utf-8");
	    echo json_encode(["status"=>"Error","message"=>"Usuario o Contraseña Incorrecta,Error al Actualizar Usuario"]);
        exit;
    }
	http_response_code(401);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"Usuario o Contraseña Incorrecta"]);
}


?>