# Julio Martinich 2-oct-2024
# glee_erp_cli.awk lee los archivos log erp Client
# v1  2-oct-24 basado en el lector de tel client
#
# awk -f glee_erp_cli.awk {archivo log} > erp_cli.csv      --- deja el resultado en erp_cli.csv
#
# en mi mac uso gawk y funciona
# GNU Awk 5.3.1, API 4.0, PMA Avon 8-g1, (GNU MPFR 4.2.1, GNU MP 6.3.0)
#
# el bloque BEGIN se ejecuta una sola vez, lo uso para poner los titulos, con ; para que sea un archivo csv leible en excel
BEGIN { 
    print "log;fechahora;mseg;tipo;tiponum;host;metodo;api;apisola;httpstatus;correlationId;clientCurrentTime;version;orderNo;itemNo;syncrotessDeliveryNumber;shipPoint;truckId;deliveryQuantity;reuseQuantity;dispatchGroup;truckName;reasonCode;cancelReason;raw";
}
function utc_to_clt(fecha_in, hora_in,    f, h, str_utc, epoch, fecha_local, hora_local, mseg) {
    split(fecha_in, f, /[\/-]/);
    split(hora_in, h, /[:.]/);
    mseg = (length(h[4]) > 0) ? h[4] : "000";

    ENVIRON["TZ"] = "UTC";
    str_utc = sprintf("%04d %02d %02d %02d %02d %02d", f[1], f[2], f[3], h[1], h[2], h[3]);
    epoch = mktime(str_utc);

    ENVIRON["TZ"] = "America/Santiago";
    fecha_local = strftime("%Y/%m/%d", epoch);
    hora_local  = strftime("%H:%M:%S", epoch);

    return fecha_local " " hora_local ";" mseg;
}

#
# este bloque se ejecuta para cada línea de entrada, $0 es la línea completa, $1, $2, ... son los tokens separados por espacio
{   
    # Extracción de algunos campos directamente por su ubicacion en el archivo
    # las ubicaciones las vi directamente inspeccionando el archivo

    # hay lineas que vienen con ctrl-M, las limpio
    linea = $0;
    gsub(/\r/,"",linea)

    # solo me intreresan los tipos de registro 145
    if ( match(linea, /145 ==/ )) {
        tiponum = 145;
        fechahora = utc_to_clt($1, $2);
        tipo = $8;
        numero = $10;

               # Extrae la parte después de "145 =="
        result = substr(linea, RSTART + RLENGTH);
        # Divide el resultado en tokens separados por espacios
        split(result, tokens, " ");
        metodo = tokens[1];
        gsub(/[\[\]]/, "", metodo); # Quita los corchetes [ y ]
        api = tokens[2];
        gsub(/,$/, "", api);        # Quita la coma final si existe

        # la api comienza con /webservices/erp/delivery/...
        if (match(api, /\/webservices\/erp\/delivery\/([^, "?]+)/, resultado )) {
            apisola = resultado[1];
        } else { apisola = ""; }

        # Host con H mayuscula expresion regular de una IP
        if (match(linea, /Host[[:space:]]*:[[:space:]]*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+)/, resultado)) {
            host= resultado[1];
        } else { host= ""; }
    
        # metadata (con soporte de espacios alrededor de :)
        # correlationId
        if (match(linea, /"correlationId"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            correlationId = resultado[1];
        } else { correlationId = ""; }
    
        # clientCurrentTime
        if (match(linea, /"clientCurrentTime"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            clientCurrentTime = resultado[1];
        } else { clientCurrentTime = ""; }
    
        # version
        if (match(linea, /"version"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            version = resultado[1];
        } else { version = ""; }
    
        # delivery
        # orderNo
        if (match(linea, /"orderNo"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            orderNo = resultado[1];
        } else { orderNo = ""; }
    
        # itemNo
        if (match(linea, /"itemNo"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            itemNo = resultado[1];
        } else { itemNo = ""; }
    
        # syncrotessDeliveryNumber
        if (match(linea, /"syncrotessDeliveryNumber"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            syncrotessDeliveryNumber = resultado[1];
        } else { syncrotessDeliveryNumber = ""; }
    
        # shipPoint
        if (match(linea, /"shipPoint"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            shipPoint = resultado[1];
        } else { shipPoint = ""; }
    
        # truckId
        if (match(linea, /"truckId"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            truckId = resultado[1];
        } else { truckId = ""; }
    
        # dispatchGroup
        if (match(linea, /"dispatchGroup"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            dispatchGroup = resultado[1];
        } else { dispatchGroup = ""; }
    
        # truckName
        if (match(linea, /"truckName"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            truckName = resultado[1];
        } else { truckName = ""; }
    
        # deliveryQuantity
        if (match(linea, /"deliveryQuantity"[[:space:]]*:[[:space:]]*([0-9.]+)/, resultado)) {
            deliveryQuantity = resultado[1];
            gsub(/\./, ",", deliveryQuantity);
        } else { deliveryQuantity = ""; }
    
        # reuseQuantity
        if (match(linea, /"reuseQuantity"[[:space:]]*:[[:space:]]*([0-9.]+)/, resultado)) {
            reuseQuantity = resultado[1];
            gsub(/\./, ",", reuseQuantity);
        } else { reuseQuantity = ""; }
    
        # cancel
        # reasonCode
        if (match(linea, /"reasonCode"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            reasonCode = resultado[1];
        } else { reasonCode = ""; }
    
        # cancelReason
        if (match(linea, /"cancelReason"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            cancelReason = resultado[1];
        } else { cancelReason = ""; }

        # me quedo con las variables guardadas y voy a la siguiente linea, que debe ser la respuesta
        raw = linea
        gsub(/;/,"|",raw)
        next;
    }

    if ( match(linea, /202 ==/ )) {
        if (match(linea, /status=([0-9]+)/, resultado)) {
            httpstatus = resultado[1];
        } else { httpstatus = ""; }

        # imprimo en una linea todos los datos separados por ; para que funcione como archivo csv
        print "SEo;" fechahora ";" tipo ";" tiponum ";" host ";" metodo ";" api ";" apisola ";" httpstatus ";" correlationId ";" clientCurrentTime ";" version ";" orderNo ";" itemNo ";" syncrotessDeliveryNumber ";" shipPoint ";" truckId ";" deliveryQuantity ";" reuseQuantity ";" dispatchGroup ";" truckName ";" reasonCode ";" cancelReason ";" raw;
    }
}

