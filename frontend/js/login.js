const URL = 'https://flask-decorassistant.herokuapp.com/';


$(document).ready(function(){

    $('#form').submit(function(e){
        e.preventDefault();
        console.log($('#form'))
        $.post(URL+'login',{
            username: $('#inputUsername').val(),
            password: $('#inputPassword').val()
        },function(data){
            console.log(data);
            data = JSON.parse(data);
            if(data.success === true){
                window.location('index.html');
            }
            else{
                console.log('There was an error with the login.')
            }
        })
    });
});