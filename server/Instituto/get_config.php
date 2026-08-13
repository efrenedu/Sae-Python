<?php

$path_token=__DIR__."/../../private/instituto/secretToken_configDb.json";
if(!file_exists($path_token)){
   http_response_code(500);
   echo json_encode(["status"=>"Error","message"=>"Data de Token de DB no Encontrada"]);
   exit;
}
$dat_token=json_decode(file_get_contents($path_token),true);
$token=$dat_token["Token"];
$headers=getallheaders();
$client_timestamp=isset($headers["X-Timestamp"])?$headers["X-Timestamp"]:"";
$client_firm=isset($headers["X-Signature"])?$headers["X-Signature"]:"";
$nonce=isset($headers["X-Nonce"])?$headers["X-Nonce"]:"";

if($client_firm=="" || $client_timestamp=="" || $nonce==""){
   http_response_code(403);
   header("Content-Type:application/json;charset=utf-8");
   echo json_encode(["status"=>"Error","message"=>"Cabecera de Autenticacion Faltantes"]);
   exit;	
}

$timestamp_server=time();
$max_dif=5;
$dif_time=abs($timestamp_server-(int)$client_timestamp);
if($dif_time>$max_dif){
	http_response_code(401);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"La peticion ha expirado","dif_segundos"=>$dif_time]);
    exit;	
}

$nonce_file=sys_get_temp_dir()."/nonce_".md5($nonce);
if(file_exists($nonce_file)){
	http_response_code(403);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"Peticion duplicada Detectada"]);
    exit;
}
file_put_contents($nonce_file,"1");
$payload=$client_timestamp."|".$nonce;

$expected_firm=hash_hmac("sha256",$payload,$token);
if(!hash_equals($expected_firm,$client_firm)){
	http_response_code(403);
	header("Content-Type:application/json;charset=utf-8");
	echo json_encode(["status"=>"Error","message"=>"La Firma HMAC Invalidad o Clave Incorrecta"]);
    exit;
}


$ruta_json=__DIR__."/../../private/instituto/config.json";
if(!file_exists($ruta_json)){
   http_response_code(500);
   echo json_encode(["status"=>"Error","message"=>"Archivo de Configuracion no Encontrado"]);
   exit;
}
header("Content-Type:application/json;charset=utf-8");
echo file_get_contents($ruta_json);

?>