<?php
session_start();
session_destroy();
header("Location: login.php"); // أو صفحة البداية
exit();
?>