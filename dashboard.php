<?php
session_start();
if(!isset($_SESSION['email'])){
    header("Location: login.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<h1>مرحباً، <?php echo $_SESSION['email']; ?>!</h1>
<p>تم تسجيل الدخول بنجاح، هذه الصفحة محمية.</p>
<a href="logout.php">تسجيل الخروج</a>
</body>
</html>