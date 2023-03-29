@isTest
private class ChatGPT_CTRLTest {
    @testSetup
    static void setup() {
        Chat_GPT_Config__c config = new Chat_GPT_Config__c();
        config.Name = 'APIToken';
        config.Auth_Token__c = 'test_token';
        insert config;
    }
    @isTest
    static void testMessageGPT() {
        Test.startTest();
        Test.setMock(HttpCalloutMock.class, new MKTChatGPTMock());
        List<String> chatMessages = new List<String>{'Hola', '¿Cómo estás?'};
        ChatGPT_CTRL.messageGPT(chatMessages);
       
        Test.stopTest();
    }
    
    @isTest
    static void testOpenApiCall() {
        String body = '{"model":"text-davinci-003", "prompt":"Mensaje de prueba", "temperature":0.7, "max_tokens":256}';
        
        Test.setMock(HttpCalloutMock.class, new MKTChatGPTMock());
        ChatGPT_CTRL.openApiCall(body);
    }
    
    @isTest
    static void testConvertPrompt() {
        List<String> chatMessages = new List<String>{'Mensaje 1', 'Mensaje 2', 'Mensaje 3'};
        String result = ChatGPT_CTRL.convertPrompt(chatMessages);
        System.assert(result.contains('Mensaje 1'));
        System.assert(result.contains('Mensaje 2'));
        System.assert(result.contains('Mensaje 3'));
    }
    
    public class MKTChatGPTMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setBody('{"choices": [{"text": "Respuesta de prueba"}]}');
            res.setStatusCode(200);
            return res;
        }
    }
}