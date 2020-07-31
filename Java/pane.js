Ext.create.('Ext.tab.Panel',
{
    width:400,

    height:400,
    plain:true,

    renderTo : document.body,
    items:[{

title : 'General',


    } ,
    {
        title: 'commands',
    }


    title : 'preview',
    xtype: 'filedcontainer',

}
);