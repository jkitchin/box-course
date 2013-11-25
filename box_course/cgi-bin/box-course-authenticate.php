<?PHP
// create .htaccess where this script is with these contents. The quotes are important!
// You have to use your own credentials from box, and set the redirect uri 
// SetEnv BOX_COURSE_CLIENT_ID "your-client-id-here"
// SetEnv BOX_COURSE_CLIENT_SECRET "your-secret-key-here"
// SetEnv BOX_COURSE_REDIRECT_URI "https://www.contrib.andrew.cmu.edu/~jkitchin/box-course-authenticate.php"
// copy box-course-authenticate.php to ~/www/box-course-authenticate.php on unix.andrew.cmu.edu. run chmod +x box-course-authenticate.php to make it executable. 
// Edit your box application in the developer site to use the redirect_uri shown above.

// READ your stuff in here.
$htaccess = file('.htaccess');
foreach ($htaccess as $line) {
  
  if (preg_match('/^\s*SetEnv\s+BOX_COURSE_CLIENT_ID\s+"([^"].*?)"\s*$/', trim($line), $matches)) 
    {
      $BOX_COURSE_CLIENT_ID = $matches[1];
    }
  if (preg_match('/^\s*SetEnv\s+BOX_COURSE_CLIENT_SECRET\s+"([^"].*?)"\s*$/', trim($line), $matches)) 
    {
      $BOX_COURSE_CLIENT_SECRET = $matches[1];
    }
  if (preg_match('/^\s*SetEnv\s+BOX_COURSE_REDIRECT_URI\s+"([^"].*?)"\s*$/', trim($line), $matches)) 
    {
      $BOX_COURSE_REDIRECT_URI = $matches[1];
    }
}


// step 2 of the authentication has 'code' in the request
if($_GET['code'])
  {
    $token_uri = 'https://www.box.com/api/oauth2/token';
    $code = $_GET['code'];
    $params = array('grant_type' => 'authorization_code',
		  'code' => $code,
		  'client_id' => $BOX_COURSE_CLIENT_ID,
		  'client_secret' => $BOX_COURSE_CLIENT_SECRET,
		  'redirect_uri' => $BOX_COURSE_REDIRECT_URI);


    $post = 'grant_type=authorization_code&code=' . $code . '&client_id=' . $BOX_COURSE_CLIENT_ID . '&client_secret=' . $BOX_COURSE_CLIENT_SECRET . '&redirect_uri=' . $BOX_COURSE_REDIRECT_URI;
    echo "one";
    $session = curl_init($token_uri);
    curl_setopt($session, CURLOPT_URL, $token_uri);
    curl_setopt($session, CURLOPT_HEADER, 0);
    curl_setopt($session, CURLOPT_POST, 1);
    curl_setopt($session, CURLOPT_POSTFIELDS, $post);
    curl_setopt($session, CURLOPT_FOLLOWLOCATION, 0);
    curl_setopt($session, CURLOPT_RETURNTRANSFER, 1);
    $result = curl_exec($session);
    curl_close($session);

    header('Content-Type: application/json');
    header('Content-Disposition: attachment; filename=token.json');

    $json = json_decode($result, true);
    $json['client_id'] = $BOX_COURSE_CLIENT_ID;
    $json['client_secret'] = $BOX_COURSE_CLIENT_SECRET;
    echo json_encode($json);
}

 else
   {
     // this is step1 in the authentication
     // this is the first step
     $uri = sprintf('https://www.box.com/api/oauth2/authorize?response_type=code&client_id=%s&client_secret=%s', $BOX_COURSE_CLIENT_ID, $BOX_COURSE_CLIENT_SECRET);

     // this redirects to box.com for username and password
     header('Location: ' . $uri);
   }
?>
