#include "FastLED.h"

#define LED_COUNT 120
#define LED_DT 2

#define MAX_BUFFER_SIZE 481
#define BLINK_PERIOD 1000
#define BLINK_TIMEOUT 2000

int max_bright = 200; // setting to 100 making cool effect
struct CRGB leds[LED_COUNT];

void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(5);
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);
  LEDS.setBrightness(max_bright);
  LEDS.addLeds<WS2812B, LED_DT, GRB>(leds, LED_COUNT);
  LEDS.show();
}

void set_all(int r, int g, int b)
{
  for (int i = 0; i < LED_COUNT; i++)
    leds[i].setRGB(r, g, b);

  LEDS.show();
}

const int maxbrt = 10;

unsigned long lastSignal = 0;

bool blinkState = 0;
unsigned long blinkTimer = 0;

void loop()
{
  if (Serial.available())
  {
    char first = Serial.read();
    if (first == '{')
    {
      lastSignal = millis();
      char data[MAX_BUFFER_SIZE];
      int amount = Serial.readBytesUntil('}', data, MAX_BUFFER_SIZE);
      data[amount] = NULL;

      char *offset = data;
      int i = 0;

      while (true)
      {
        int brt = atoi(offset);
        brt = min(brt, max_bright);

        /* Pink */
        leds[i++].setRGB(brt, map(brt, 0, 255, 0, 100), brt);

        /* Green-Red */
        // leds[i++].setRGB(brt, 255-brt, 255-brt);

        offset = strchr(offset, '|');
        if (offset)
          offset++;
        else
          break;
      }
      LEDS.show();
    }
  }
  else
  {
    if (millis() - lastSignal <= BLINK_TIMEOUT
    ||  millis() - blinkTimer <= BLINK_PERIOD)
      return;

    set_all(0, 0, 0);
    blinkTimer = millis();
    leds[0].setRGB(0, 0, blinkState ? 2 : 0);
    blinkState ^= 1;
    LEDS.show();
  }
}
