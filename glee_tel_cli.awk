# Julio Martinich 1-oct-2024
# glee_tel_cli.awk lee los archivos log telematic Client
# v1  2-oct-24 basado en el lector de erp server
#
# Opciones de hora:
# awk -v tz=UTC -f glee_tel_cli.awk {archivo log} > tel_cli.csv      --- convierte UTC a CLT (default)
# awk -v tz=CLT -f glee_tel_cli.awk {archivo log} > tel_cli.csv      --- no convierte la hora (CLT)
#
# en mi mac uso gawk y funciona
# GNU Awk 5.3.1, API 4.0, PMA Avon 8-g1, (GNU MPFR 4.2.1, GNU MP 6.3.0)
#
# el bloque BEGIN se ejecuta una sola vez, lo uso para poner los titulos, con ; para que sea un archivo csv leible en excel
BEGIN { 
    print "log;fechahora;mseg;tipo;tiponum;metodo;api;apisola;httpstatus;host;msgId;version;timeStamp;subOrgID;requestID;licensePlate;syncrotessDeliveryNumber;syncrotessDeliveryNumberCancel;orderSubType;locationID;reasonCode;radius;latitude;longitude;erpTicketNumber;mess;raw";
}
function format_time(fecha_in, hora_in,    f, h, str_utc, epoch, fecha_local, hora_local, mseg) {
    split(fecha_in, f, /[\/-]/);
    split(hora_in, h, /[:.]/);
    mseg = (length(h[4]) > 0) ? h[4] : "000";

    if (tz == "CLT") {
        return sprintf("%04d/%02d/%02d %02d:%02d:%02d;%s", f[1], f[2], f[3], h[1], h[2], h[3], mseg);
    } else {
        ENVIRON["TZ"] = "UTC";
        str_utc = sprintf("%04d %02d %02d %02d %02d %02d", f[1], f[2], f[3], h[1], h[2], h[3]);
        epoch = mktime(str_utc);

        ENVIRON["TZ"] = "America/Santiago";
        fecha_local = strftime("%Y/%m/%d", epoch);
        hora_local  = strftime("%H:%M:%S", epoch);

        return fecha_local " " hora_local ";" mseg;
    }
}

#
# este bloque se ejecuta para cada línea de entrada, $0 es la línea completa, $1, $2, ... son los tokens separados por espacio
{   
    # Extracción de algunos campos directamente por su ubicacion en el archivo
    # las ubicaciones las vi directamente inspeccionando el archiv    # hay lineas que vienen con ctrl-M, las limpio
    linea = $0;
    gsub(/\r/,"",linea)

    # solo me interesan los tipos de registro 145 ==
    if ( match(linea, /145 ==/ )) {
        tiponum = 145;
        fechahora = format_time($1, $2);
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

        # la api comienza con /webservices/telematics/...
        if (match(api, /\/webservices\/telematics\/([^, "?]+)/, resultado )) {
            apisola = resultado[1];
        } else { apisola = ""; }
    
        # host en minusculas expresion regular de una IP y puerto
        if (match(linea, /Host[[:space:]]*:[[:space:]]*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+)/, resultado)) {
            host= resultado[1];
        } else { host= ""; }

        # msgId
        if (match(linea, /"msgId"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            msgId = resultado[1];
        } else { msgId = ""; }
    
        # sttVersion
        if (match(linea, /"sttVersion"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            sttVersion = resultado[1];
        } else { sttVersion = ""; }
    
        # timeStamp
        if (match(linea, /"timeStamp"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            timeStamp = resultado[1];
        } else { timeStamp = ""; }
    
        # subOrgID
        if (match(linea, /"subOrgID"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            subOrgID = resultado[1];
        } else { subOrgID = ""; }
    
        # requestID
        if (match(linea, /"requestID"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            requestID = resultado[1];
        } else { requestID = ""; }
    
        # vehicleNumber
        if (match(linea, /"vehicleNumber"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            vehicleNumber = resultado[1];
        } else { vehicleNumber = ""; }
    
        # orderSubType
        if (match(linea, /"orderSubType"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            orderSubType = resultado[1];
        } else { orderSubType = ""; }
    
        # locationID
        if (match(linea, /"locationID"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            locationID = resultado[1];
        } else { locationID = ""; }
    
        # reasonCode
        if (match(linea, /"reasonCode"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            reasonCode = resultado[1];
        } else { reasonCode = ""; }
    
        # syncrotessDeliveryNumber en cancel (en formato array ["..."])
        if (match(linea, /"syncrotessDeliveryNumber"[[:space:]]*:[[:space:]]*\["([^"]+)"\]/, resultado)) {
            syncrotessDeliveryNumberCancel= resultado[1];
        } else { syncrotessDeliveryNumberCancel= ""; }
    
        # syncrotessDeliveryNumber en assignment
        if (match(linea, /"syncrotessDeliveryNumber"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            syncrotessDeliveryNumber= resultado[1];
        } else { syncrotessDeliveryNumber= ""; }

        if ( syncrotessDeliveryNumber == "" ) {
            syncrotessDeliveryNumber = syncrotessDeliveryNumberCancel;
        }

        # erpTicketNumber
        if (match(linea, /"erpTicketNumber"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            erpTicketNumber= resultado[1];
        } else { erpTicketNumber= ""; }

        # messageText
        if (match(linea, /"messageText"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            mess = resultado[1];
            gsub(/;/, "", mess);
        } else { mess = ""; }

        # unloadingLocation
        if (match(linea, /"unloadingLocation"[[:space:]]*:[[:space:]]*\{(.*)\}/, resultado)) {
            unloadingLocation= resultado[1];
            if (match(unloadingLocation, /"radius"[[:space:]]*:[[:space:]]*([0-9.]+)/, resultado)) {
                radius=resultado[1];
            } else { radius = ""}
            if (match(unloadingLocation, /"latitude"[[:space:]]*:[[:space:]]*(-?[0-9.]+)/, resultado)) {
                latitude=resultado[1];
                gsub(/\./, ",", latitude)
            } else { latitude = ""}
            if (match(unloadingLocation, /"longitude"[[:space:]]*:[[:space:]]*(-?[0-9.]+)/, resultado)) {
                longitude=resultado[1];
                gsub(/\./, ",", longitude)
            } else { longitude = ""}
        } else {
            unloadingLocation= "";
            radius = "";
            latitude = "";
            longitude = "";
        }
       
        raw = linea
        gsub(/;/,"|",raw)    
        # me quedo con las variables guardadas y voy a la siguiente linea, que debe ser la respuesta
        next;
    }

    if ( match(linea, /202 ==/ )) {
        if (match(linea, /status=([0-9]+)/, resultado)) {
            httpstatus = resultado[1];
        } else { httpstatus = ""; }

        # imprimo en una linea todos los datos separados por ; para que funcione como archivo csv
        print "STo;" fechahora ";" tipo ";" tiponum ";" metodo ";" api ";" apisola ";" httpstatus ";" host ";" msgId ";" sttVersion ";" timeStamp ";" subOrgID ";" requestID ";" vehicleNumber ";" syncrotessDeliveryNumber ";" syncrotessDeliveryNumberCancel ";" orderSubType ";" locationID ";" reasonCode ";" radius ";" latitude ";" longitude ";" erpTicketNumber ";" mess ";" raw ;
    }
}
