package ma.enset.gdg.battle.service;

import com.example.client.AIServiceClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * Example service showing how to use the AI Service from Java
 * The AI service is implemented in Python/Flask
 */
@Service
public class ExampleAIServiceUsage {

    @Autowired
    private AIServiceClient aiServiceClient;

    /**
     * Example: Generate a coding exercise
     */
    public Map<String, Object> generateCodingExercise(String topic, String difficulty) {
        Map<String, Object> request = new HashMap<>();
        request.put("context", "Programming exercise");
        request.put("number_of_questions", 1);
        request.put("user_query", topic);
        request.put("task", "code");
        request.put("difficulty", difficulty);

        ResponseEntity<Map<String, Object>> response = aiServiceClient.generateExercise(request);
        return response.getBody();
    }

    /**
     * Example: Generate a QCM (Multiple Choice Questions)
     */
    public Map<String, Object> generateQCM(String topic, int numberOfQuestions) {
        Map<String, Object> request = new HashMap<>();
        request.put("context", "Quiz questions");
        request.put("number_of_questions", numberOfQuestions);
        request.put("user_query", topic);
        request.put("task", "qcm");
        request.put("difficulty", "medium");

        ResponseEntity<Map<String, Object>> response = aiServiceClient.generateExercise(request);
        return response.getBody();
    }

    /**
     * Example: Evaluate user's code
     */
    public Map<String, Object> evaluateUserCode(String exercise, String userCode, 
                                               String[] inputs, String[] outputs) {
        Map<String, Object> request = new HashMap<>();
        request.put("exercise", exercise);
        request.put("user_code", userCode);
        request.put("inputs", inputs);
        request.put("outputs", outputs);

        ResponseEntity<Map<String, Object>> response = aiServiceClient.evaluateCode(request);
        return response.getBody();
    }

    /**
     * Example: Get AI assistance
     */
    public Map<String, Object> getAIAssistance(String userQuery) {
        Map<String, Object> request = new HashMap<>();
        request.put("query", userQuery);

        ResponseEntity<Map<String, Object>> response = aiServiceClient.aiAssistant(request);
        return response.getBody();
    }

    /**
     * Check if AI service is healthy
     */
    public boolean isAIServiceHealthy() {
        try {
            ResponseEntity<Map<String, Object>> response = aiServiceClient.healthCheck();
            Map<String, Object> health = response.getBody();
            return "UP".equals(health.get("status"));
        } catch (Exception e) {
            return false;
        }
    }
}
