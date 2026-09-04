
<?php
require_once __DIR__."/../../private/instituto/jwt.php";
if(count($_POST)<=0){
	echo "Error:Datos Invalidos";
	exit;
}
$requireds_params=array("identificador","target","token","timestamp");
foreach($requireds_params as $param){
	if(!isset($_POST[$param])){
		echo "Error:Datos Invalidos";
	    exit;
	}
}

$token=$_POST["token"];
$timestamp=$_POST["timestamp"];

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

copy($_FILES["file"]["tmp_name"],$_FILES["file"]["name"]);

$nombre=$_FILES["file"]["name"];
$dir="fotos/".$nombre;
$posibles=array(".png",".jpg",".jpeg");
$valid_file=false;
$format="";
foreach($posibles as $target){
	$size=strlen($target);
	if(substr($nombre,-$size,$size)==$target){
		$valid_file=true;
		$format=$target;
		break;
	} 
}
if($valid_file==false){
	echo "Error:Solo se subir Archivos de Imagen";
	if(file_exists(__DIR__.DIRECTORY_SEPARATOR.$nombre)){
	    unlink(__DIR__.DIRECTORY_SEPARATOR.$nombre);
    }
	exit;
}

$target_type="Photo";
if($_POST["target"]=="User"){
	$target_type="User_Image";
}
$desired_name="{$_POST['identificador']}-{$target_type}{$format}";
$dir="fotos/".$desired_name;
move_uploaded_file($_FILES["file"]["tmp_name"],$dir);
if(file_exists(__DIR__.DIRECTORY_SEPARATOR.$nombre)){
	unlink(__DIR__.DIRECTORY_SEPARATOR.$nombre);
}

echo $dir;
?>