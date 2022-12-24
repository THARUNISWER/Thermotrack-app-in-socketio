coreTemp=document.getElementById('core-temp')
skinTemp=document.getElementById('skin-temp')
HSValue=document.getElementById('HS-value')
maxHSvalue=document.getElementById('maxHS-value')
kcalValue=document.getElementById('kcal-value')
msg=document.getElementById('msg-to-display')
minute_dis = document.getElementById('min')
time=document.getElementById('time-value')
statIndicator=document.getElementsByClassName('list-read')
battery_view=document.getElementById('percentage-indictor')
container = document.getElementById('color_change_container')
weight = document.getElementById('input-bar-weight')
document.getElementById("recovery").style.display = "none";
document.getElementById("flags").style.display = "none";


    console.log('hi');

     percentage = HSValue.innerHTML
     height=parseInt(((parseInt(percentage))*206/100))+'px'
     console.log(height)
     battery_view.style.height=height

     list_color=['#de6d6d','#99ba64','#d9d9d9']
     var recovery = document.getElementById('recovery').innerHTML
     //console.log(recovery)
     if (recovery==0) {
        container.style.backgroundColor = list_color[0];
         msg.innerHTML='maxHS in'
     }else if (recovery==1) {
         container.style.backgroundColor = list_color[1];
         msg.innerHTML='Recovery in'
     }
     else{
         container.style.backgroundColor = list_color[1];
         msg.innerHTML='No stress'
         minute_dis.style.display = "none"
         time.style.display = "none"
     }

     var sensor_flags = document.getElementById('flags').innerHTML
     for (var i = 0; i < statIndicator.length; i++) {
        //console.log(sensor_flags[i])
         if(sensor_flags[i]=='0'){
            statIndicator[i].style.backgroundColor = list_color[0]
         }
         else if(sensor_flags[i] == '1'){
            statIndicator[i].style.backgroundColor = list_color[1]
         }
     }


