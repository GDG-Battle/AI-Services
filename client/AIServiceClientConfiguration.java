package ma.enset.gdg.battle.common.client;

import feign.Logger;
import feign.Request;
import feign.Retryer;
import feign.codec.ErrorDecoder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

/**
 * Configuration for AI Service Feign Client
 * Provides custom configuration for timeouts, retries, and error handling
 * 
 * @author GDG Battle Team
 * @version 1.0
 */
@Configuration
public class AIServiceClientConfiguration {

    /**
     * Configure request timeouts for AI service calls
     * AI operations might take longer due to processing complexity
     */
    @Bean
    public Request.Options requestOptions() {
        return new Request.Options(
            30, TimeUnit.SECONDS, // connect timeout
            60, TimeUnit.SECONDS, // read timeout
            true // follow redirects
        );
    }

    /**
     * Configure retry policy for failed requests
     * AI service calls should be retried with backoff
     */
    @Bean
    public Retryer retryer() {
        return new Retryer.Default(
            1000, // initial retry interval in ms
            3000, // max retry interval in ms
            3     // max attempts
        );
    }

    /**
     * Configure logging level for debugging
     * Use BASIC for production, FULL for development
     */
    @Bean
    public Logger.Level feignLoggerLevel() {
        return Logger.Level.BASIC;
    }

    /**
     * Custom error decoder for AI service responses
     * Handles specific AI service error codes and messages
     */
    @Bean
    public ErrorDecoder errorDecoder() {
        return new AIServiceErrorDecoder();
    }
}
