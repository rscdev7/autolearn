Search.setIndex({docnames:["abstract_event_sourcing","async_kafka_consumer","concrete_event_sourcing","domain_work","event_sourcing_utility","exception_manager","index","kafka_logger","logger","mongo_engine","network_serializer","rabbit_consumer","service_config","service_set_up","service_utility","singleton","time_stamp_manager"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["abstract_event_sourcing.rst","async_kafka_consumer.rst","concrete_event_sourcing.rst","domain_work.rst","event_sourcing_utility.rst","exception_manager.rst","index.rst","kafka_logger.rst","logger.rst","mongo_engine.rst","network_serializer.rst","rabbit_consumer.rst","service_config.rst","service_set_up.rst","service_utility.rst","singleton.rst","time_stamp_manager.rst"],objects:{"session.lib.abstract_event_sourcing":{DomainEntity:[0,0,0,"-"],DomainEvent:[0,0,0,"-"],EventStore:[0,0,0,"-"]},"session.lib.abstract_event_sourcing.DomainEntity":{DomainEntity:[0,1,1,""]},"session.lib.abstract_event_sourcing.DomainEntity.DomainEntity":{__abstractmethods__:[0,2,1,""],__slots__:[0,2,1,""],apply:[0,3,1,""],emit:[0,3,1,""],init:[0,3,1,""],reset:[0,3,1,""],rewind:[0,3,1,""]},"session.lib.abstract_event_sourcing.DomainEvent":{DomainEvent:[0,1,1,""]},"session.lib.abstract_event_sourcing.DomainEvent.DomainEvent":{__init__:[0,3,1,""]},"session.lib.abstract_event_sourcing.EventStore":{EventStore:[0,1,1,""]},"session.lib.abstract_event_sourcing.EventStore.EventStore":{__abstractmethods__:[0,2,1,""],__slots__:[0,2,1,""],read:[0,3,1,""],start:[0,3,1,""],stop:[0,3,1,""],write:[0,3,1,""]},"session.lib.async_kafka_consumer":{AsyncKafkaConsumer:[1,0,0,"-"]},"session.lib.async_kafka_consumer.AsyncKafkaConsumer":{AsyncKafkaConsumer:[1,1,1,""]},"session.lib.async_kafka_consumer.AsyncKafkaConsumer.AsyncKafkaConsumer":{__init__:[1,3,1,""],consume:[1,3,1,""],start:[1,3,1,""],stop:[1,3,1,""]},"session.lib.concrete_event_sourcing":{AutoLearnLogEntity:[2,0,0,"-"],KafkaEventStore:[2,0,0,"-"]},"session.lib.concrete_event_sourcing.AutoLearnLogEntity":{AutoLearnLogEntity:[2,1,1,""]},"session.lib.concrete_event_sourcing.AutoLearnLogEntity.AutoLearnLogEntity":{__abstractmethods__:[2,2,1,""],__slots__:[2,2,1,""],apply:[2,3,1,""],emit:[2,3,1,""],init:[2,3,1,""],reset:[2,3,1,""],rewind:[2,3,1,""]},"session.lib.concrete_event_sourcing.KafkaEventStore":{KafkaEventStore:[2,1,1,""]},"session.lib.concrete_event_sourcing.KafkaEventStore.KafkaEventStore":{__abstractmethods__:[2,2,1,""],read:[2,3,1,""],start:[2,3,1,""],stop:[2,3,1,""],write:[2,3,1,""]},"session.lib.domain_work":{worker:[3,0,0,"-"]},"session.lib.domain_work.worker":{check_session_exist:[3,4,1,""],decryptIdSession:[3,4,1,""],guard:[3,4,1,""],launcher:[3,4,1,""],queryOneRecord:[3,4,1,""],save_session:[3,4,1,""],session_record_guard:[3,4,1,""],session_update_guard:[3,4,1,""],shut_down_system:[3,4,1,""],view_sessions:[3,4,1,""]},"session.lib.event_sourcing_utility":{event_sourcing_utility:[4,0,0,"-"]},"session.lib.event_sourcing_utility.event_sourcing_utility":{final_communication_log:[4,4,1,""],getLocalLogger:[4,4,1,""],make_behavioral_event:[4,4,1,""],setUpEventSourcing:[4,4,1,""]},"session.lib.exception_manager":{ExceptionManager:[5,0,0,"-"]},"session.lib.exception_manager.ExceptionManager":{ExceptionManager:[5,1,1,""]},"session.lib.exception_manager.ExceptionManager.ExceptionManager":{lookForExceptions:[5,3,1,""]},"session.lib.kafka_logger":{KafkaLogger:[7,0,0,"-"]},"session.lib.kafka_logger.KafkaLogger":{KafkaLogger:[7,1,1,""]},"session.lib.kafka_logger.KafkaLogger.KafkaLogger":{__init__:[7,3,1,""],log:[7,3,1,""],start:[7,3,1,""],stop:[7,3,1,""]},"session.lib.logger":{Logger:[8,0,0,"-"]},"session.lib.logger.Logger":{Logger:[8,1,1,""]},"session.lib.logger.Logger.Logger":{__init__:[8,3,1,""],error:[8,3,1,""],log:[8,3,1,""],start:[8,3,1,""]},"session.lib.mongo_engine":{MongoEngine:[9,0,0,"-"]},"session.lib.mongo_engine.MongoEngine":{MongoEngine:[9,1,1,""]},"session.lib.mongo_engine.MongoEngine.MongoEngine":{__init__:[9,3,1,""],count:[9,3,1,""],push:[9,3,1,""],pushBinary:[9,3,1,""],query:[9,3,1,""],queryOnes:[9,3,1,""],queryOnesBinary:[9,3,1,""],start:[9,3,1,""],stop:[9,3,1,""],update:[9,3,1,""]},"session.lib.network_serializer":{NetworkSerializer:[10,0,0,"-"]},"session.lib.network_serializer.NetworkSerializer":{NetworkSerializer:[10,1,1,""]},"session.lib.network_serializer.NetworkSerializer.NetworkSerializer":{__init__:[10,3,1,""],buildNewKey:[10,3,1,""],decodeBinaryObj:[10,3,1,""],decodeJson:[10,3,1,""],decryptField:[10,3,1,""],encodeBinaryObj:[10,3,1,""],encodeJson:[10,3,1,""],encryptField:[10,3,1,""],readKeyFromFile:[10,3,1,""]},"session.lib.rabbit_consumer":{RabbitConsumer:[11,0,0,"-"]},"session.lib.rabbit_consumer.RabbitConsumer":{RabbitConsumer:[11,1,1,""]},"session.lib.rabbit_consumer.RabbitConsumer.RabbitConsumer":{__init__:[11,3,1,""],consume:[11,3,1,""],start:[11,3,1,""],stop:[11,3,1,""]},"session.lib.service_config":{ServiceConfig:[12,0,0,"-"]},"session.lib.service_config.ServiceConfig":{ServiceConfig:[12,1,1,""]},"session.lib.service_config.ServiceConfig.ServiceConfig":{BROKER_LOGIN_TOKEN:[12,2,1,""],DB_COLLECTION:[12,2,1,""],DB_HOST_NAME:[12,2,1,""],DB_NAME:[12,2,1,""],DB_PASSWORD:[12,2,1,""],DB_PORT:[12,2,1,""],DB_USER_NAME:[12,2,1,""],ENTITY_ID:[12,2,1,""],EVENT_STORE_NAME:[12,2,1,""],EVENT_STORE_PORT:[12,2,1,""],RECORD_GUARD_PARTITION:[12,2,1,""],RECORD_GUARD_TOPIC:[12,2,1,""],RECORD_QUEUE:[12,2,1,""],REST_EP_PARTITION:[12,2,1,""],REST_EP_TOPIC:[12,2,1,""],STORAGE_RECORD_QUEUE:[12,2,1,""],UPDATE_GUARD_PARTITION:[12,2,1,""],UPDATE_GUARD_TOPIC:[12,2,1,""],UPDATE_QUEUE:[12,2,1,""],__slots__:[12,2,1,""],inspect:[12,3,1,""]},"session.lib.service_set_up":{system_set_up:[13,0,0,"-"]},"session.lib.service_set_up.system_set_up":{set_up_guard:[13,4,1,""],set_up_rest_end_point:[13,4,1,""]},"session.lib.service_utility":{utils:[14,0,0,"-"]},"session.lib.service_utility.utils":{ser_model__db_2_net:[14,4,1,""],ser_model__net_2_db:[14,4,1,""]},"session.lib.singleton":{Singleton:[15,0,0,"-"]},"session.lib.singleton.Singleton":{Singleton:[15,1,1,""]},"session.lib.singleton.Singleton.Singleton":{__call__:[15,3,1,""],__init__:[15,3,1,""]},"session.lib.time_stamp_manager":{TimeStampManager:[16,0,0,"-"]},"session.lib.time_stamp_manager.TimeStampManager":{TimeStampManager:[16,1,1,""]},"session.lib.time_stamp_manager.TimeStampManager.TimeStampManager":{currentTimeStampInMS:[16,3,1,""],currentTimeStampInSec:[16,3,1,""],date2Timestamp:[16,3,1,""],timestamp2Date:[16,3,1,""],timestampMs2Sec:[16,3,1,""],timestampSec2Ms:[16,3,1,""]}},objnames:{"0":["py","module","Python modulo"],"1":["py","class","Python classe"],"2":["py","attribute","Python attributo"],"3":["py","method","Python metodo"],"4":["py","function","Python funzione"]},objtypes:{"0":"py:module","1":"py:class","2":"py:attribute","3":"py:method","4":"py:function"},terms:{"0":16,"02":16,"03":1,"05":[7,16],"07":[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],"08":1,"09":7,"15":[8,10],"16":[5,9,11],"2021":[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],"23":[7,8,9,11],"24":[1,16],"25":[0,2,4,5,15],"28":4,"29":10,"31":[3,12,13,14],"5":3,"abstract":0,"byte":10,"class":[0,1,2,4,5,7,8,9,10,11,12,15,16],"int":[0,1,2,3,4,7,9,16],"static":[5,16],In:[0,3,4],La:3,None:[0,1,2,3,4,7,8,9,10,11,12],Per:15,Se:16,_:[0,2],__abstractmethods__:[0,2],__call__:15,__init__:[0,1,7,8,9,10,11,15],__slots__:[0,2,12],_collectionnamegener:9,_config:12,_entityid:[0,2],_eventlist:[0,2],_eventstor:[0,2],_readmodel:0,_status:[0,2],_writemodel:0,abc:[0,15],abcmet:15,abstract_event_sourcing:[0,2,4],accad:5,acced:9,adatt:14,affront:3,aggiorn:[3,9],aggiung:10,aio_pik:11,altriment:[4,5],altro:3,andar:7,anno:16,anzic:15,apac:[1,7],apirouter:13,applic:[0,2,3,4,8,13],apply:[0,2],archiv:3,argoment:15,args:[0,2,15],arrest:3,asincr:1,asincron:3,assenz:14,assoc:[0,2,3,4,16],astrazion:0,async:[0,1,2,3,4,7,9,11],async_kafka_consumer:1,asynci:3,asynckafkaconsumer:6,atriment:16,attiv:8,attual:16,autent:3,author:[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],autolearnlogentity:[3,4,6,13],avent:3,avvi:[0,1,2,9,11,13],azion:4,background:4,bas:[0,1,2,5,7,8,9,10,11,12,15,16],bases:15,bianr:9,binar:[9,10],bisogn:5,bool:[0,2,3,4,5,16],broker:[1,2,7],broker_login_token:12,bson:9,build:[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],buildnewkey:10,bytes:[0,2,4,7,10],call:15,camb:[0,2],camp:[9,10,15],cas:[0,2,15],catalog:4,cerc:6,check_session_exist:3,chiamant:[3,14],chiar:10,chiav:[3,4,7,10],chiud:[2,7],chiusur:[1,4],cifr:[3,10],cifratur:[3,10],client:4,cls:15,cod:[3,11],codif:10,codific:10,colleg:10,collezion:9,com:[9,15,16],component:[0,1,2,3,4,5,7,8,9,11,12,13,15,16],comportamental:4,comput:13,comun:4,concret:2,concrete_event_sourcing:[2,4,13],configur:[0,3,4,7,8,12,13],connesion:2,connession:[0,1,3,4,7,9],connett:7,consum:[1,3,11],consumer:1,cont:9,conten:[2,12],contenent:10,content:[13,14],conterr:[3,15],contien:[3,10],controll:[3,5],convert:[9,14,16],correl:0,corrent:12,corrispett:3,corrott:3,corutin:3,costru:4,costrutt:15,costruttor:[0,1,7,8,9,10,11,15],count:9,creazion:1,crittograf:10,crittotest:10,currenttimestampinms:16,currenttimestampinsec:16,d:8,dat:[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],databas:3,date2timestamp:16,datetim:16,db:[3,9,14],db_collection:12,db_host_nam:12,db_nam:12,db_password:12,db_port:12,db_user_nam:12,decifr:10,decifratur:[3,10],decodebinaryobj:10,decodejson:10,decodif:10,decryptfield:10,decryptidsession:3,def:[0,1,2,9,10,16],deriv:[0,2,3,4,14],deserializz:10,design:[0,15],destin:4,dict:[0,1,2,3,4,7,9,10,11,13,14,15],disc:10,disconnesion:[0,2],disconnession:3,dispon:1,divent:15,dizionar:[0,2,9,10],document:9,domain_work:3,domainentity:[2,6],domainevent:[2,4,6],domin:0,duplic:[0,2],durant:1,eccezion:[0,1,2,3,4,5,7,9,10,11,12,14,16],eccezzion:[3,8,11],effettu:4,effettur:4,emett:[0,2],emit:[0,2],encodebinaryobj:10,encodejson:10,encryptfield:10,entit:[0,2],entity_id:12,error:[0,1,2,3,8],esegu:7,esist:3,esper:3,espress:16,esser:14,estrarr:3,event:[0,2,3,4,13],event_sourcing_utility:6,event_store_nam:12,event_store_params:3,event_store_port:12,eventsourcing:4,eventstor:[2,4,6],eventual:[0,2,3],evit:[0,2],exception:[0,1,2,3,4,7,8,9,10,11,12,14,16],exception_manager:5,exceptionmanager:6,exceptions:11,excpetion:7,fa:[4,9],fals:[0,2,3,4,5,16],fann:9,far:[3,8,13,15],fastap:[4,13],fatt:7,fil:[8,10,12],final_communication_log:4,flag:[0,2],form:[0,2,3,10,14,16],formatt:16,forn:13,fra:7,fri:[5,7,8,9,11],frozenset:[0,2],funzion:[3,4,10,13,14,16],gener:[7,8,9,10,11],gest:[3,5],getlocallogger:4,giorn:16,gir:[7,9],groupid:1,guard:[3,13],hann:[0,2],host:[1,7,9],host_nam:2,id:3,identif:0,identific:0,implement:[1,2,3,15],impost:16,inammiss:16,incapsul:16,incominc:7,indic:[6,9,16],inform:[0,13],init:[0,2],inizial:[0,2],inizializz:[0,2,4],inoltr:[9,10],inser:[3,7,9],inspect:12,interess:1,interfacc:[0,2,3,4,15],intern:[7,8],intim:3,invi:7,istanz:15,json:10,kafk:[1,2,3,4,7],kafka_logger:7,kafkaeventstor:[3,4,6,13],kafkalogger:6,key:[0,2,15],kwargs:[0,2,15],lanc:[3,13],last:[0,1,2,3,4,5,8,9,11,12,13,14,15],last_upd:[7,10,16],lat:13,launcher:3,layer:13,leg:2,legg:[0,9,10,12],leggittim:3,lettur:[0,1,2,3,10,12],lib:[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],line:8,list:[0,1,2,3,9,15],local:[3,4,13],log:[2,4,7,8],logg:[11,13],logger:[3,4,6,13],loggin:4,logging:[4,8],lookforexceptions:5,make_behavioral_event:4,mal:3,mantien:[0,3,13],matc:9,memorizz:12,men:3,mer:[8,13],mes:16,messagg:[1,3,4,8,11,14],metod:[0,1,2,3,5,7,8,9,10,11,15,16],microserviz:[3,4,8,12,13,14],millisecond:16,min:16,ml:14,mobil:16,mod:[0,2,3,4],modell:14,modif:[0,2,3,4],modific:[0,2,15],modul:[4,14],molt:[0,2,16],mon:8,mong:[3,9],mongo_engin:[3,9],mongodb:[3,14],mongoengin:[3,6],monitor:3,nam:[1,15],namespac:15,necessar:[0,3,4],network_serializer:[3,10],networkserializer:[3,6],nom:[4,7,8,9,11],number:1,numer:[9,16],nuov:[3,10],obbiett:0,object:[0,1,2,5,7,8,9,10,11,12,15,16],objectid:9,occorrent:9,offset:2,oggett:[0,2,3,4,10,12,13,16],ogni:[3,9],oltre:16,opportun:5,oppur:[3,4],optional:[0,2,3,9],opzion:[3,13],ora:16,originar:9,outlearn:4,parametr:[0,1,2,3,4,5,7,8,9,10,11,13,14,15,16],part:3,particol:[0,3,4],partition:2,partizion:[1,7],pass:[3,4,9,14,15,16],password:9,path:[8,10],pattern:[0,15],payload:[0,2,4,7],pbinaryfields:9,pbinobject:10,pbrokernam:[1,7],pbrokerport:[1,7],pcfg:3,pcollectionnam:9,pcomtyp:4,pday:16,pdb:3,pdbengin:3,pdbnam:9,pdestid:4,pdestinationserv:4,pdict:10,pdocs:9,pentityid:[0,2],permanent:3,permantn:3,permett:[0,2,3,4,5,7,10,13,14,15],persist:[0,2],persistent:13,pevent:[0,2],peventpayload:0,peventstor:[0,2,4],peventstoreparams:4,peventtimestamp:0,pfield:10,pfieldstobinary:9,pgroupid:1,pguardtyp:3,phostnam:9,phour:16,pidsession:3,pkey:[4,7],plogger:3,plogintoken:11,plogpath:8,pmessagetyp:4,pminutes:16,pmonth:16,pmsg:8,pmstimestamp:16,pnam:8,pnetworklogger:4,pobject:10,port:[1,2,7,9],possibil:7,pparams:[0,2,3],ppartition:[1,7],ppassword:9,ppayload:[4,10],pport:9,pproducer:3,pprojection:9,pquery:9,pqueu:3,pqueuenam:11,prabbitconsumer:3,precedent:7,precord:[7,14],prel:[0,2,4],prelev:[3,11],present:[2,3,8,10,14],presenz:3,presult:5,prewindmod:[0,2],prim:9,probabil:[0,2,16],problem:[0,2,3],process:[3,9,13],produttor:3,proiezion:9,psecretkeypath:10,pserializer:3,pservic:4,pservicenam:4,psourceserv:4,pstringout:16,ptimestamp:[4,7,16],ptopic:1,ptopicnam:7,ptype:[3,13],pupd:9,pusernam:9,push:9,pushbinary:9,pye:16,pymong:9,python:[10,15],quand:9,quell:[3,4],query:[3,9],queryonerecord:3,queryones:9,queryonesbinary:9,quest:[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],queu:3,queueempty:11,queues:3,rabbit_consumer:[3,11],rabbit_producer:3,rabbitconsumer:[3,6],rabbitmq:[3,11],rabbitproducer:3,racchiud:14,raccogl:[0,4],rappresent:[0,2,4,10,16],read:[0,2],readkeyfromfil:10,receiv:4,record:[1,3,4,7,9,14],record_guard_partition:12,record_guard_topic:12,record_queu:12,recuper:[3,9,11],registr:3,regol:[0,2],reset:[0,2],resett:[0,2],rest:13,rest_ep_partition:12,rest_ep_topic:12,restitu:[3,9,13,16],results:9,ret:14,rewind:[0,2,4],ricerc:[3,9],richiest:[3,4],ricostru:[0,2],risied:9,rispost:4,ristrett:15,risult:[5,9],ritorn:[0,1,2,3,4,5,7,8,9,10,11,12,13,14,16],router:13,routing:13,rscal:[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],runtim:5,salv:[3,10],sar:[7,15],sat:[1,3,12,13,14,16],save_session:3,scatur:[0,1,2,16],scelt:1,scritt:14,scrittur:[0,2,3,4,10],scriv:[0,2,3,4,7,8,9],second:16,segnal:[0,2,8],seguent:[3,4],selezion:9,send:4,ser:[3,4,13,14],ser_model__db_2_net:14,ser_model__net_2_db:14,serializz:[3,10],serv:[5,7,8,9,11,12,16],server:4,service_config:[3,12,13],service_set_up:13,service_utility:6,serviceconfig:[3,6,13],serviz:4,session:[0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16],session_record_guard:[3,13],session_update_guard:[3,13],sessionrecord:3,sessionupd:3,set_up_guard:13,set_up_rest_end_point:13,setupeventsourcing:4,sfrutt:[0,2,3],shut_down_system:3,singleton:6,sistem:[0,3,4],soddisf:9,soll:[0,1,2,3,4,7,8,9,10,11,12,14,16],sommar:9,son:[4,5],sorgent:4,sourcing:[0,3,4,13],specif:[3,7],start:[0,1,2,7,8,9,11],stat:[0,2,3,4],stdout:8,stop:[0,1,2,7,9,11],stopp:[0,1,9,11],stor:[0,2,13],storag:3,storage_record_queu:12,storageconfig:13,storagerecord:3,str:[0,1,2,3,4,7,8,9,10,11,13,15,16],string:[10,16],sub:0,sun:[0,2,4,5,7,15,16],support:10,sync:4,system_set_up:6,tal:[0,2,3,4,7,15],tant:[2,15],task:[3,4],test:10,thu:[1,10],time_stamp_manager:16,timestamp2d:16,timestamp:[0,2,4,7,16],timestamp_ms:2,timestampmanager:6,timestampms2sec:16,timestampsec2ms:16,tip:[3,4,5,9,10,11,13,15,16],token:[9,11],topic:[1,2,7],trasform:9,tre:4,trov:3,trovat:9,tru:16,tupl:[3,13],tutt:[0,1,2,3,9],ugual:3,ultim:[0,2,4],unic:15,union:[0,1,2,3,7,8,9,10,11,12,14,16],univoc:0,unix:16,updat:[0,1,2,3,4,5,8,9,11,12,13,14,15],update_guard_partition:12,update_guard_topic:12,update_queu:12,updateresult:9,utent:9,util:[3,14],utility:[3,4],utilizzer:4,utils:14,valu:[0,2,15],ver:[4,5,16],verific:[0,3,4,5,8],viagg:14,vicevers:16,vien:0,view_sessions:3,virgol:16,vogl:15,volt:[3,7],vuol:[3,9],vuot:11,wed:4,worker:6,writ:[0,2]},titles:["DomainEntity","AsyncKafkaConsumer","AutoLearnLogEntity","worker","event_sourcing_utility","ExceptionManager","Benvenuto nella Documentazione di session","KafkaLogger","Logger","MongoEngine","NetworkSerializer","RabbitConsumer","ServiceConfig","system_set_up","service_utility","Singleton","TimeStampManager"],titleterms:{and:6,asynckafkaconsumer:1,autolearnlogentity:2,benven:6,document:6,domainentity:0,domainevent:0,event_sourcing_utility:4,eventstor:0,exceptionmanager:5,indices:6,kafkaeventstor:2,kafkalogger:7,logger:8,modul:6,mongoengin:9,networkserializer:10,rabbitconsumer:11,service_utility:14,serviceconfig:12,session:6,singleton:15,system_set_up:13,tables:6,timestampmanager:16,worker:3}})