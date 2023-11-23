#include "FastLED.h"

#define LED_COUNT 120
#define LED_DT 2 /* data pin */

#define MAX_BUFFER_SIZE 721 /* bytes */
#define MAX_BRIGHTNESS 40   /* 0 - 255 */

struct CRGB leds[LED_COUNT];

void setup() {
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);

  Serial.begin(9600);
  Serial.setTimeout(5);

  FastLED.setBrightness(255);
  FastLED.addLeds<WS2812B, LED_DT, GRB>(leds, LED_COUNT);
  FastLED.show();
}

unsigned long lastSignal = 0;

void loop() {
  if (Serial.available()) {
    if (Serial.read() == '{') {
      lastSignal = millis();

      char data[MAX_BUFFER_SIZE];
      int amount = Serial.readBytesUntil('}', data, MAX_BUFFER_SIZE);
      data[amount] = NULL;

      uint8_t r, g, b = 0;
      int i = 0;
      char *offset;

      Serial.print("{");
      Serial.print(data);
      Serial.print("}");

      offset = strtok(data, "|");
      i = constrain(atoi(offset), 0, 119);

      offset = strtok(NULL, "|");
      r = constrain(atoi(offset), 0, MAX_BRIGHTNESS);

      offset = strtok(NULL, "|");
      g = constrain(atoi(offset), 0, MAX_BRIGHTNESS);

      offset = strtok(NULL, "|");
      b = constrain(atoi(offset), 0, MAX_BRIGHTNESS);

      leds[i].setRGB(r, g, b);

    }
  } else {
    if (millis() - lastSignal > 1000)
      for (int i = 0; i < LED_COUNT; i++) leds[i].setRGB(0, 0, 0);
  }
  FastLED.show();
}
