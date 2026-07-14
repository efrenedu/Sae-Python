<?php


$base_directory = "";
$file_to_delete="";
if(isset($_GET['directorio'])){
  $base_directory=$_GET['directorio'];	
}
if(isset($_GET['nombre'])){
  $file_to_delete=$_GET['nombre'];	
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