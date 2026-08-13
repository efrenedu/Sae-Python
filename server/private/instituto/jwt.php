<?php

function base64UrlEncode($data){
	return rtrim(strtr(base64_encode($data),'+/','-_'),'=');
}
function base64UrlDecode($data){
	return base64_decode(strtr($data,'-_','+/'));
}

function generate_tokenLogin($data_user,$secret_key,$duration_seconds=3600){
	$header=json_encode(["typ"=>"JWT","Alg"=>"HS256"]);
	$actual_time=time();
	$expiration_time=$actual_time+$duration_seconds;
	$payload=json_encode([
	  "iat"=>$actual_time,
	  "exp"=>$expiration_time,
	  "CI_trabaj"=>$data_user["CI_trabaj"],
	  "Acceso"=>$data_user["Nivel_Acceso"],
	  "Id_usr"=>$data_user["Id_User"]
	]);
	$base64_header=base64UrlEncode($header);
	$base64_payload=base64UrlEncode($payload);
	$signature=hash_hmac("sha256",$base64_header.".".$base64_payload,$secret_key,true);
	$base64_signature=base64UrlEncode($signature);
	return $base64_header.".".$base64_payload.".".$base64_signature;
		
}
function validar_token($token_jwt,$secret_key){
	$token_parts=explode(".",$token_jwt);
	if(count($token_parts)!==3){
		return ["Valido"=>"False","Message"=>"Formato de Token Invalido"];
	}
	$header_token=$token_parts[0];
	$payload_token=$token_parts[1];
	$signature_token=$token_parts[2];
	$signature=hash_hmac("sha256",$header_token.".".$payload_token,$secret_key,true);
	$base64_signature=base64UrlEncode($signature);
	if(!hash_equals($base64_signature,$signature_token)){
		return ["Valido"=>"False","Message"=>"Firma de Token no Valida"];
	}
	$payload_data=json_decode(base64UrlDecode($payload_token),true);
	$error_exp=false;
	if(!isset($payload_data["exp"])){
		return ["Valido"=>"False","Message"=>"Data Faltante en Payload"];
	}
	if($payload_data["exp"]<time()){
		return ["Valido"=>"False","Message"=>"Token Expirado"];
	}
	return[
	 "Valido"=>"True",
	 "Message"=>$payload_data
	];
}

?>