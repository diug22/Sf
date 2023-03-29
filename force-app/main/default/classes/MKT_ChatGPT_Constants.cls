public class MKT_ChatGPT_Constants {

    public static final string API = 'https://api.openai.com/v1/completions';
    public static final string ContentType = 'application/json';
    public static final string AuthToken = Chat_GPT_Config__c.getValues('APIToken').Auth_Token__c;
    public static final string Model = 'text-davinci-003';
    public static final Decimal Temperature = 0.7;
    public static final Integer MaxTokens = 256;
    public static final string PromptUser = '\n Usuario-';
    public static final string PromptIA = '\n IA-';
    public static final string Prompt = 'Un usuario esta dentro de la plataforma de salesforce y se ha configurado un chat para ayudarle en sus tareas. Le pregunta a un chat de IA experto en Salesforce.';
}