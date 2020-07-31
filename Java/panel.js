
<html>
<head>
<title>Hello World Window</title>
<link rel="stylesheet" type="text/css" href="ext-3.0.0/resources/css/ext-all.css" />
<script type="text/javascript" src="ext-3.0.0/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="ext-3.0.0/ext-all.js"></script>

</head>
<body>
<script type="text/javascript">

Ext.onReady(function() {

    var panel1 = {                                          
        html   : 'I am Panel1',
        id     : 'panel1',
        frame  : true,
        height : 100
    }
    var panel2 = {
        html  : '<b>I am Panel2</b>',
        id     : 'panel2',
        frame : true
    }
    
    var myWin = new Ext.Window({                            
        id     : 'myWin',
        height : 400,
        width  : 400,
        items  : [
            panel1,
            panel2
        ]
    });
    
    myWin.show();
    

});
</script> 
<div id='div1'>asdf</div>
</body>
</html>

   