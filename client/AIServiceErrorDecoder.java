package ma.enset.gdg.battle.common.client;

import feign.Response;
import feign.codec.ErrorDecoder;
import ma.enset.gdg.battle.common.exception.AIServiceException;
import ma.enset.gdg.battle.common.exception.AIServiceUnavailableException;
import ma.enset.gdg.battle.common.exception.InvalidRequestException;
import org.springframework.http.HttpStatus;

/**
 * Custom error decoder for AI Service Feign client
 * Handles specific error responses from the AI service
 * 
 * @author GDG Battle Team
 * @version 1.0
 */
public class AIServiceErrorDecoder implements ErrorDecoder {

    private final ErrorDecoder defaultErrorDecoder = new Default();

    @Override
    public Exception decode(String methodKey, Response response) {
        HttpStatus status = HttpStatus.valueOf(response.status());
        
        switch (status) {
            case BAD_REQUEST:
                return new InvalidRequestException(
                    "Invalid request to AI service: " + extractErrorMessage(response)
                );
            case SERVICE_UNAVAILABLE:
            case INTERNAL_SERVER_ERROR:
                return new AIServiceUnavailableException(
                    "AI service is currently unavailable: " + extractErrorMessage(response)
                );
            case REQUEST_TIMEOUT:
                return new AIServiceException(
                    "AI service request timeout: " + extractErrorMessage(response)
                );
            default:
                return defaultErrorDecoder.decode(methodKey, response);
        }
    }

    private String extractErrorMessage(Response response) {
        try {
            if (response.body() != null) {
                return response.body().toString();
            }
        } catch (Exception e) {
            // If we can't read the body, return a generic message
        }
        return "Unknown error occurred";
    }
}
