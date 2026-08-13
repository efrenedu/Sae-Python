<?php
//get the conection from DataBase
function get_conexion(){
	
   $path_config=__DIR__."/config.json";
   if(!file_exists($path_config)){
	    return  array("response"=>-1,"data"=>"");
   }
   $config=json_decode(file_get_contents($path_config),true);
   $host=$config["host"];
   $user=$config["user"];
   $db=$config["db_name"];
   $pass=$config["password"];
   $conexion=mysqli_connect($host,$user,$pass);
   if (mysqli_connect_errno()) {
      return array("response"=>-2,"data"=>"");
  }
   mysqli_select_db($conexion,$db); 
   if (mysqli_connect_errno()) {
	 return array("response"=>-2,"data"=>"");
   }
   return array("response"=>0,"conector"=>$conexion,"db"=>$db);
}

?>