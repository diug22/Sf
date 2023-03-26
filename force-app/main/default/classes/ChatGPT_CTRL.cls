public with sharing class ChatGPT_CTRL {
    
        @AuraEnabled(cacheable=true)
        public static void messageGPT(List<String> chatMessages) {
            String body = new MKT_ChatGPT_Wrapper.BodyToChat(convertPrompt(chatMessages)).getBody();
            openApiCall(body);
        }
        
        @Future(callout=true)
        public static void openApiCall(String body){
            system.debug(body);
            HttpRequest req = new HttpRequest();
            HttpResponse res = new HttpResponse();
            Http http = new Http();
            req.setEndpoint(MKT_ChatGPT_Constants.API);
            req.setMethod('GET');
            req.setHeader('Content-Type', MKT_ChatGPT_Constants.ContentType);
            req.setHeader('Authorization',MKT_ChatGPT_Constants.AuthToken);
            req.setBody(body);
            req.setTimeout(120000);
            try {
                res = http.send(req);
                if(res.getStatusCode() == 200) {
                        MKT_ChatGPT_Wrapper.ResponseChat response = (MKT_ChatGPT_Wrapper.ResponseChat)JSON.deserialize(res.getBody(),MKT_ChatGPT_Wrapper.ResponseChat.class);
                        GPTChat__e chat = new GPTChat__e();
                        chat.text__c = response.choices[0].text;
                        EventBus.publish(chat);
                }
            } catch(System.CalloutException e) {
                System.debug('Callout error: '+ e);
            }
        }
		
    	@TestVisible
        private static string convertPrompt(List<String> chatMessages){
            String prompt = MKT_ChatGPT_Constants.Prompt;
            for(integer i=0;i<chatMessages.size();i++){
                String whotalk = Math.mod(i,2) == 0 ? MKT_ChatGPT_Constants.PromptUser : MKT_ChatGPT_Constants.PromptIA;
                prompt += whotalk + chatMessages[i];
            }
            prompt += MKT_ChatGPT_Constants.PromptIA;
            return prompt;
        }
}