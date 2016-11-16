<?php
	header("Content-Type: text/html; charset=utf-8");
	header("X-UA-Compatible: IE=Edge,chrome=1");
	header("Access-Control-Allow-Origin: *");
	header("Access-Control-Allow-Methods: POST,GET,PUT,DELETE,OPTIONS");
	header("Access-Control-Allow-Headers: Accept, Origin, Content-type, Authorization");
?>
<!DOCTYPE html>
<html>
<head>
	<meta base="/">
	<link rel="stylesheet" type="text/css" href="deps/bootstrap/dist/css/bootstrap.min.css"/>


	<script src="deps/jquery.min.js?v=1.7.1"></script>
	<script src="deps/jquery.once.js?v=1.2"></script>
	<script src="deps/drupal.js"></script>
	<script src="deps/contextual.js"></script>
	<script src="deps/admin_menu.js"></script>
	<script src="deps/admin_menu_toolbar.js"></script>
	<script src="deps/chart.min.js"></script>
	<script src="ntxuva.js"></script>
</head>
<body>
<?php
	require_once("page--inqueritos.tpl.php");
?>
	<script src="deps/bootstrap/dist/js/bootstrap.min.js"></script>
</body>
</html>