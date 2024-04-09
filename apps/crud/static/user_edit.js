var vali_message={
    username : {
        none : "사용자명은 필수입니다.",
        length : "30문자 이내로 입력해 주세요."
    },
    email : {
        none : "메일 주소는 필수입니다.",
        regex : "메일 주소의 형식으로 입력해 주세요."
    }, 
    password : {
        none : "비밀번호는 필수입니다."
    }

}

function user_regist_go(){
   
    for (var div of document.querySelectorAll('div.vali')){ div.remove();}
    var submit_ok = true;
    form =document.querySelector("form[role='form']");
    
    for (var element of form){
        //alert(element.name);
        if(!element.value){
            make_message_span(element,vali_message[element.name].none);
            submit_ok = false;
            continue;
        }


        switch(element.name){
            case "username":
                if(element.value.length > 30){ 
                    make_message_span(element,vali_message[element.name].length);
                    submit_ok = false;
                }
            break;
            case "email":
                let regexp = /[a-z0-9]+@[a-z]+\.[a-z]{2,3}/g;
                if(!element.value.match(regexp)){ 
                    make_message_span(element,vali_message[element.name].regex);
                    submit_ok = false;
                }
            break;
        }
        
    }
    return submit_ok;
}

function make_message_span(target, message){
    let div = document.createElement('div');
    div.classList.add("vali")

    let span = document.createElement('span');
    span.style.color='red';
    span.innerHTML = message;

    div.append(span);
    
    target.after(div);
    
}

var setPassword = "";

function input_password(){
    //alert(setPassword);
    document.querySelector("input[name='password']").value = setPassword;
}


document.querySelector("button[btn-role='delete']").onclick=function(event){
    //alert("click delete");
    //location.href = "/crud/users/{{user.id}}/delete";
    //var form = new FormData();
    //form.action = "/crud/users/{{user.id}}/delete";
    //form.method = "POST";
    //form.submit();

    const btn = event.currentTarget;

    $.ajax({
        url : "/crud/users/"+btn.id+"/delete",
        method:"post",
        success:function(url){
            //console.log(data);
            location.href = url;
        }
    });
}
