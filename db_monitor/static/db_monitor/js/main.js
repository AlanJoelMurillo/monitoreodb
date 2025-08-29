// Coloca los colores de las luces (Verde o gris)
function change_colors(){
$servers_list = document.getElementsByClassName("db-data")

Array.from($servers_list).forEach(server =>{
    const status = String(server.querySelector(".light").textContent)
    const $ligth = server.querySelector(".server")

    if (status === "running"){  
        $ligth.classList.remove("pending")
        $ligth.classList.add("running")
    } else if (status === "down"){
        $ligth.classList.add("pending")
        $ligth.classList.remove("running")

    }  
})
}
change_colors()

//

//Revisa el estado de las conexiones cada minuto
function check_status(){
    fetch('/check_status')
    .then(response => response.json())
    .then(responseJSON =>{
        data = responseJSON.data
        for(const key in data ){
            if (data.hasOwnProperty(key)){
                const $server = document.getElementById(`server-${data[key].id}`)
                if ($server.textContent === data[key].status){
                    
                }else{
                    if ($server.textContent === "running"){$server.textContent = "down"} 
                    else{$server.textContent = "running"}
                }
            }
        }
    const isoDate = responseJSON.time
    const dateObj = new Date(isoDate)

    const optionsTime = {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12:false,
        timezone:"America/Ciudad_Juarez"
    }
    const newTime = new Intl.DateTimeFormat("es-ES",optionsTime).format(dateObj)

    const optionsDate = {
            day: "2-digit",
            month: "short",
            year: "numeric",
            timezone:"America/Ciudad_Juarez"
        }
        const newDate = new Intl.DateTimeFormat("es-ES",optionsDate).format(dateObj)
    document.getElementById("date").textContent = "Última actualización: "+newTime +" - " + newDate
    change_colors()
    console.log("checked")    })
}


setInterval(check_status,10000)

