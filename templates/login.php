<?php
session_start();

// بيانات الدخول الصحيحة (تقدرين تغيّريها)
$users = [
    "user@example.com" => "1234"
];

$error = "";

// تحقق من الفورم
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';

    if(isset($users[$email]) && $users[$email] === $password) {
        $_SESSION['email'] = $email;
        header("Location: dashboard.php"); // تحويل للصفحة المحمية
        exit(); // لازم بعد header
    } else {
        $error = "البريد الإلكتروني أو كلمة المرور خطأ.";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <title>webpage Design</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="main">
    <div class="navbar">
        <div class="icon">
            <h2 class="logo">Bank</h2>
        </div>
        <div class="menu">
            <ul>
                <li><a href="#">Home</a></li>
                <li><a href="#">About</a></li>
                <li><a href="#">Services</a></li>
                <li><a href="#">Design</a></li>
                <li><a href="#">Contact</a></li>
            </ul>
        </div>
        <div class="search">
            <input class="srch" type="search" placeholder="type to text">
            <a href="#"><button class="btn">Search</button></a>
        </div>
    </div>

    <div class="content">
        <h1>welcome to <br><span> our bank </span> </br></h1>
        <p class="par">Your financial partner for a better future.</p>
        <button class="cn"><a href="#">Join Now</a></button>

        <div class="form">
            <h2>Login Here</h2>

            <!-- رسالة الخطأ -->
            <?php if($error) echo "<p style='color:red;'>$error</p>"; ?>

            <!-- الفورم -->
            <form method="POST" action="login.php">
                <input type="email" name="email" placeholder="Enter Email Here" required>
                <input type="password" name="password" placeholder="Enter Password Here" required>
                <button type="submit" class="btnn">Login</button>
            </form>

            <p class="link">Don't have an account? <a href="#">Sign Up</a></p>
            <p class="liw">log in with</p>

            <div class="icon">
                <a href="#"><ion-icon name="logo-facebook"></ion-icon></a>
                <a href="#"><ion-icon name="logo-twitter"></ion-icon></a>
                <a href="#"><ion-icon name="logo-google"></ion-icon></a>
                <a href="#"><ion-icon name="logo-instagram"></ion-icon></a>
                <a href="#"><ion-icon name="logo-skype"></ion-icon></a>
            </div>
        </div>
    </div>
</div>

<script src="https://unpkg.com/ionicons@5.4.0/dist/ionicons.js"></script>
</body>
</html>