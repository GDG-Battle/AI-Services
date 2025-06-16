package ma.enset.gdg.battle.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.Map;

/**
 * Simple Feign client for AI Service
 * This is a basic example for Java services that need to call the Python AI service
 * 
 * Note: The AI service is implemented in Python/Flask
 * This client provides a simple interface for Java services to communicate with it
 */
@FeignClient(name = "ai-service")
public interface AIServiceClient {

    /**
     * Generate code exercises or QCM
     * @param request Map containing: context, number_of_questions, user_query, task, difficulty
     * @return Generated exercise response
     */
    @PostMapping("/generate")
    ResponseEntity<Map<String, Object>> generateExercise(@RequestBody Map<String, Object> request);

    /**
     * Evaluate user code submission
     * @param request Map containing: exercise, user_code, inputs, outputs
     * @return Evaluation result with feedback
     */
    @PostMapping("/evaluate")
    ResponseEntity<Map<String, Object>> evaluateCode(@RequestBody Map<String, Object> request);

    /**
     * AI assistant for queries
     * @param request Map containing: query
     * @return AI response
     */
    @PostMapping("/aiassistant")
    ResponseEntity<Map<String, Object>> aiAssistant(@RequestBody Map<String, Object> request);

    /**
     * Health check
     * @return Service health status
     */
    @GetMapping("/health")
    ResponseEntity<Map<String, Object>> healthCheck();

    /**
     * Service information
     * @return Service info
     */
    @GetMapping("/actuator/info")
    ResponseEntity<Map<String, Object>> serviceInfo();
}
