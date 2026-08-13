<?php

//verify Integrity of Data Received
require_once __DIR__."/../../private/instituto/jwt.php";
if(count($_POST)<3){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes","Redirect_Panel"=>"No Redirect"]);
   exit;	
}
if(!isset($_POST["token"]) || !isset($_POST["timestamp"]) || !isset($_POST["target_panel"])){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Datos Faltantes","Redirect_Panel"=>"No Redirect"]);
   exit;
}

$token_client=$_POST["token"];
$client_timestamp=$_POST["timestamp"];
$target_panel=$_POST["target_panel"];

//Verify Timestamp of Client
$timestamp_server=time();
$max_dif=5;
$dif_time=abs($timestamp_server-(int)$client_timestamp);
if($dif_time>$max_dif){
	http_response_code(401);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"La peticion ha expirado","dif_segundos"=>$dif_time,"Redirect_Panel"=>"No Redirect"]);
    exit;	
}

//get the permits of Panels Data of Server
$path_data_permit=__DIR__."/../../private/instituto/permit_panels.json";
if(!file_exists($path_data_permit)){
    http_response_code(500);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Error Obteniendo data de Permisos del Servidor","Redirect_Panel"=>"No Redirect"]);
    exit;
}   

$permit_data=json_decode(file_get_contents($path_data_permit),true);
if(!array_key_exists($target_panel,$permit_data)){
   http_response_code(400);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Id de Pantalla Invalida","Redirect_Panel"=>"No Redirect"]);
   exit;
}
$target_permits=$permit_data[$target_panel];
if($token_client=="" ){
	$valid_panel=false;
	if(count($target_permits)>0){
		if($target_permits[0]=="none"){
			$valid_panel=true;
		}
	}
	if($valid_panel==false){
        $path_login_panel=__DIR__."/../../private/instituto/UI_Json/inicio.json";
        if(!file_exists($path_login_panel)){
           http_response_code(500);
           header("Content-Type:application/json;charset=utf-8");
           echo json_encode(["status"=>"Error","message"=>"Acceso Denegado al Panel,Error Inesperado Obtieniendo Datos del Panel de Login","Redirect_Panel"=>"No Redirect"]);
           exit;
        }  
		$data=json_decode(file_get_contents($path_login_panel),true);
        http_response_code(400);
        header("Content-Type:application/json;charset=utf-8");
		echo json_encode(["status"=>"Invalid Access","message"=>"Acceso Denegado al Panel","data"=>$data,"Redirect_Panel"=>"inicio"]);
        exit;
	}
	$path_offline_panel=__DIR__."/../../private/instituto/UI_Json/".$target_panel.".json";
    if(!file_exists($path_offline_panel)){
       http_response_code(500);
       header("Content-Type:application/json;charset=utf-8");
       echo json_encode(["status"=>"Error","message"=>"Error  Datos del Panel","Redirect_Panel"=>"No Redirect"]);
       exit;
    }  
	$data=json_decode(file_get_contents($path_offline_panel),true);
	http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Success","message"=>"OK","data"=>$data,"Redirect_Panel"=>"No Redirect"]);
    exit;
}

//get the Secret Key of Server
$path_secret_key=__DIR__."/../../private/instituto/secretToken.json";
if(!file_exists($path_secret_key)){
    http_response_code(500);
    header("Content-Type:application/json;charset=utf-8");
    echo json_encode(["status"=>"Error","message"=>"Error Obteniendo data de Configuracion del Token del Servidor","Redirect_Panel"=>"No Redirect"]);
    exit;
}   

$data_secretKey=json_decode(file_get_contents($path_secret_key),true);
$valid_token=validar_token($token_client,$data_secretKey["Token"]);
//Verify the Token of User if is Invalid send the Login/Inicio Panel Data
if($valid_token["Valido"]=="False"){
	$path_login_panel=__DIR__."/../../private/instituto/UI_Json/inicio.json";
    if(!file_exists($path_login_panel)){
       http_response_code(500);
       header("Content-Type:application/json;charset=utf-8");
       echo json_encode(["status"=>"Error","message"=>$valid_token["Message"].", Error Inesperado Obtieniendo Datos del Panel de Login","Redirect_Panel"=>"inicio"]);
       exit;
    }  
    $data=json_decode(file_get_contents($path_login_panel),true);
    http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Invalid Token","message"=>$valid_token["Message"],"data"=>$data,"Redirect_Panel"=>"No Redirect"]);
    exit;
}

$client_access=$valid_token["Message"]["Acceso"];
$valid_panel=false;
for ($i=0;$i<count($target_permits);$i++){
	if($target_permits[$i]==$client_access){
		$valid_panel=true;
		break;
	}
}
if($valid_panel==false){
	$path_welcome=__DIR__."/../../private/instituto/UI_Json/welcome.json";
    if(!file_exists($path_welcome)){
        http_response_code(500);
        header("Content-Type:application/json;charset=utf-8");
        echo json_encode(["status"=>"Error","message"=>"Acceso Denegado al Panel,Error Inesperado Obtieniendo Datos del Panel de Login","Redirect_Panel"=>"No Redirect"]);
        exit;
    }  
    $data=json_decode(file_get_contents($path_welcome),true);
    http_response_code(400);
    header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Invalid Access","message"=>"Acceso Denegado al Panel","data"=>$data,"Redirect_Panel"=>"welcome"]);
    exit;
}

$path_panel=__DIR__."/../../private/instituto/UI_Json/".$target_panel.".json";
if(!file_exists($path_panel)){
     http_response_code(500);
	 header("Content-Type:application/json;charset=utf-8");
	 echo json_encode(["status"=>"Error","message"=>"Data del Panel no Encontrada","Redirect_Panel"=>"No Redirect"]);
     exit;
}


http_response_code(400);
header("Content-Type:application/json;charset=utf-8"); 
$data=json_decode(file_get_contents($path_panel),true);
echo json_encode(["status"=>"Success","message"=>"OK","data"=>$data,"Redirect_Panel"=>"No Redirect"]);
exit;

?>