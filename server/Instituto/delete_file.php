<?php

require_once __DIR__."/../../private/instituto/jwt.php";
if(count($_GET)<=0){
	echo "Error:Datos Invalidos";
	exit;
}
$requireds_params=array("directorio","nombre","token","timestamp");
foreach($requireds_params as $param){
	if(!isset($_GET[$param])){
		echo "Error:Datos Invalidos";
	    exit;
	}
}


$token=$_GET["token"];
$timestamp=$_GET["timestamp"];

//Verify TimeStamp
$timestamp_server=time();
$max_dif=5;
$dif_time=abs($timestamp_server-(int)$timestamp);
if($dif_time>$max_dif){
	echo "Error:Tiempo Expirado";
	exit;	
}

$path_secret_key=__DIR__."/../../private/instituto/secretToken.json";
if(!file_exists($path_secret_key)){
   echo "Error:erro Leyendo Token del Servidor";
   exit;
}   

$data_secretKey=json_decode(file_get_contents($path_secret_key),true);
$valid_token=validar_token($token,$data_secretKey["Token"]);
//Verify the Token of User if is Invalid send the Login/Inicio Panel Data
if($valid_token["Valido"]=="False"){
	echo "Error:Acceso Denegado ";
	exit;
}

$base_directory = "";
$file_to_delete="";
$base_directory=$_GET['directorio'];	
$file_to_delete=$_GET['nombre'];	

$posibles=array(".pdf",".xlsx");
$valid_file=false;
foreach($posibles as $target){
	$size=strlen($target);
	if(substr($file_to_delete,-$size,$size)==$target){
		$valid_file=true;
		break;
	} 
}
if($valid_file==false){
	echo "Error:Solo se puede Borrar Formatos ";
	exit;
}


if (is_file($file_to_delete) && $base_directory!="" ){
  $path =$base_directory.$file_to_delete;
  chown($path, 667);
  if(unlink($path)){
    echo "File Deleted";
  }
  else{
     echo "fail";
   }
}
else{
 if($base_directory==""){
	echo "No directorio ";
 }
 else{
   echo "No File found";
 }
}
?>