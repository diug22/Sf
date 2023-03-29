@isTest
public class ChatGPT_CTRLTest {
    
    @TestSetup
    static void setup() {
        Chat_GPT_Config__c config = new Chat_GPT_Config__c(
            Name = 'APIToken',
            Auth_Token__c = 'test_token'
        );
        insert config;
    }
    
    public class MKT_ChatGPT_WrapperMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setBody('{"choices": [{"text": "Test response"}]}');
            res.setStatusCode(200);
            return res;
        }
    }
    
    @isTest
    static void testMessageGPT() {
        Test.startTest();
        Test.setMock(HttpCalloutMock.class, new MKT_ChatGPT_WrapperMock());
        List<String> chatMessages = new List<String>{'Hello', 'How are you?'};
        ChatGPT_CTRL.messageGPT(chatMessages);
        Test.stopTest();
    }
    
    @isTest
    static void testOpenApiCall() {
        Test.startTest();
        Test.setMock(HttpCalloutMock.class, new MKT_ChatGPT_WrapperMock());
        String body = '{"model": "text-davinci-002", "prompt": "Test prompt", "temperature": 0.7, "max_tokens": 150}';
        ChatGPT_CTRL.openApiCall(body);
        Test.stopTest();
    }
    
    @isTest
    static void testConvertPrompt() {
        List<String> chatMessages = new List<String>{'Hello', 'How are you?'};
        String prompt = ChatGPT_CTRL.convertPrompt(chatMessages);
        System.assertEquals('ChatGPT: Hello\nUser: How are you?\nChatGPT: ', prompt);
    }
}