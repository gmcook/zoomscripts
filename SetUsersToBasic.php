<?php
//This script loops over a .csv list of user IDs(usually emails) from Zoom and sets their license to Basic (delicenses them from costing money for Zoom enterprise customers)
require 'ZoomAPIWrapper.php';
//enter JWT token key/secret created in Zoom Admin
$apiKey = '';
$apiSecret = '';

$zoom = new ZoomAPIWrapper( $apiKey, $apiSecret );
$userUpdateDetails = array(
  "type"  => "1",
);
$userToUpdate='';
$licSuccess=0;
$licFailure=0;
$tokSuccess=0;
$tokFailure=0;
$path= 'log.txt';

if (($handle = fopen('listofusers.csv', 'r')) !== FALSE) { // Check the resource is valid
  while (($users = fgetcsv($handle, 1000, ",")) !== FALSE) { // Check opening the file is OK!
      for ($i = 0; $i < count($users); $i++) { // Loop over the data using $i as index pointer
          $userToUpdate=$users[$i];
          $tokendeletion = "skipped deleting token" . "\n";
          echo $userToUpdate;
          $response = $zoom->doRequest('PATCH','/users/{userId}',array(),array('userId'=>$userToUpdate),$userUpdateDetails);
          // On success the response from Zoom in this case is empty.
          // We can test for success by checking the response code
          if ($zoom->responseCode()==204) {
              $setlicense = "License Set to Basic For " . $userToUpdate . "\n";
              $licSuccess++;
              unset($response);
              $response = $zoom->doRequest('DELETE','/users/{userId}/token',array(),array('userId'=>$userToUpdate));
              if($zoom->responseCode()==204){
                $tokendeletion = "Token Deleted For " . $userToUpdate . "\n";
                $tokSuccess++;
                }
              else{
                $tokendeletion="Token Deletion Failed For " . $userToUpdate . "\n";
                $tokFailure++;
                }

          } else {
                $setlicense="Setting License failed for " . $userToUpdate . "\n";
                $licFailure++;
                print_r($response);
                }
        file_put_contents($path, $setlicense, FILE_APPEND);
        echo $setlicense;
        echo $tokendeletion;
        
        file_put_contents($path, $tokendeletion, FILE_APPEND);
        
      }
  }
  fclose($handle);
        echo "Licenses set successfully for " . $licSuccess . "\n";
        echo "Licenses were not set for " . $licFailure . "\n";
        echo "Tokens successfull deleted for " . $tokSuccess . "\n";
        echo "Tokens failed to deleted for " . $tokFailure . "\n";
}


?>