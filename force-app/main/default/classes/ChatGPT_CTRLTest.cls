@isTest
private class ChatGPT_CTRLTest {
    


    private class GPTAPI_MockHttpResponse implements HttpCalloutMock{
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', MKT_ChatGPT_Constants.ContentType);
            res.setStatusCode(200);
            res.setBody('{"choices": [{"text": "Respuesta de prueba"}]}');
            return res;
        }
    }
    
    private static void createChatGPT_Config() {
        Chat_GPT_Config__c config = new Chat_GPT_Config__c();
        config.Name = 'APIToken';
        config.Auth_Token__c =  'test';
        insert config;
    }
    
    @isTest
    static void testMessageGPT() {
        createChatGPT_Config();
        Test.startTest();
        
        List<String> chatMessages = new List<String>();
        chatMessages.add('What is Salesforce?');
        ChatGPT_CTRL.messageGPT(chatMessages);
        
        Test.stopTest();
    }
    
    @isTest
    static void testOpenApiCall() {
        createChatGPT_Config();
        String body = '{"model": "text-davinci-003","prompt": "Test de prompt","temperature": 0.7,"max_tokens": 256}';
        
        Test.startTest();
        Test.setMock(HttpCalloutMock.class, new GPTAPI_MockHttpResponse());
        ChatGPT_CTRL.openApiCall(body);
        Test.stopTest();
    }
    
    @isTest
    static void testConvertPrompt() {
        createChatGPT_Config();

        List<String> chatMessages = new List<String>();
        chatMessages.add('¿Cuál es la finalidad de Salesforce?');
        
        String expectedResult = 'Un usuario esta dentro de la plataforma de salesforce y se ha configurado un chat para ayudarle en sus tareas. Le pregunta a un chat de IA experto en Salesforce.\n Usuario-¿Cuál es la finalidad de Salesforce?\n IA-';
        String result = ChatGPT_CTRL.convertPrompt(chatMessages);
        
        System.assertEquals(expectedResult,result);
    }
}
