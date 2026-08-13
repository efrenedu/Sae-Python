
<?php
copy($_FILES["file"]["tmp_name"],$_FILES["file"]["name"]);

$nombre=$_FILES["file"]["name"];
$dir="expedientes/".$nombre;
move_uploaded_file($_FILES["file"]["tmp_name"],$dir);
if(file_exists(__DIR__.DIRECTORY_SEPARATOR.$nombre)){
	unlink(__DIR__.DIRECTORY_SEPARATOR.$nombre);
}

echo $dir;
?>