#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

typedef struct __attribute__((packed)) {
    unsigned int   packetNumber;
    unsigned char  packetStatus;
    float    pressure1;
    float    pressure2;
    float    altitude1;
    float    altitude2;
    float    altitudeDifference;
    float    descentSpeed;
    float    temperature;
    float    batteryVoltage;
    float    gpsLatitude;
    float    gpsLongitude;
    float    gpsAltitude;
    float    pitch;
    float    roll;
    float    yaw;
    float    rhrh;
    float    iotData1;
    float    iotData2;
    unsigned char  checksum;
} TelemetryPacket;

float random_float(float min, float max) {
    float scale = rand() / (float) RAND_MAX;
    return min + scale * ( max - min );
}

int main() {
    int sockfd;
    struct sockaddr_in targetAddr;

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    memset(&targetAddr, 0, sizeof(targetAddr));
    targetAddr.sin_family = AF_INET;
    targetAddr.sin_port = htons(5005);

    if (inet_pton(AF_INET, "192.168.1.124", &targetAddr.sin_addr) <= 0) {
        perror("Invalid address / Address not supported");
        exit(EXIT_FAILURE);
    }

    printf("--- macOS C Smart Satellite Simulation Started ---\n");
    printf("Target: 192.168.1.124 Port: 5005\n");
    printf("Packet Size: %lu bytes\n\n", sizeof(TelemetryPacket));

    TelemetryPacket packet;
    int counter = 1;
    srand(time(NULL));

    float simAltitude = 1250.0;
    int separationOccurred = 0;
    int filterWorking = 1;

    while(1) {
        packet.packetNumber = counter;

        simAltitude -= random_float(5.0, 10.0);
        if (simAltitude < 0) {
            simAltitude = 1250.0;
            separationOccurred = 0;
        }
        packet.altitude1 = simAltitude;
        packet.gpsAltitude = simAltitude;

        if (rand() % 5 == 0) packet.descentSpeed = random_float(14.5, 16.0);
        else packet.descentSpeed = random_float(12.1, 13.9);

        if (rand() % 5 == 0) packet.iotData1 = random_float(3.0, 5.5);
        else packet.iotData1 = random_float(6.1, 7.9);

        if (rand() % 10 == 0) packet.pressure1 = 0.0f;
        else packet.pressure1 = 1013.25f + random_float(-2.0, 2.0);

        if (rand() % 10 == 0) {
            packet.gpsLatitude = 0.0f;
            packet.gpsLongitude = 0.0f;
        } else {
            packet.gpsLatitude = 39.7804f;
            packet.gpsLongitude = 32.8048f;
        }

        if (simAltitude < 400.0) separationOccurred = 1;

        filterWorking = (rand() % 15 != 0);

        packet.pressure2 = 1012.80f;
        packet.altitude2 = simAltitude + 2.0f;
        packet.altitudeDifference = 0.0f;
        packet.temperature = 24.5f;
        packet.batteryVoltage = 7.6f;
        packet.pitch = random_float(-5, 5);
        packet.roll = random_float(-5, 5);
        packet.yaw = random_float(0, 360);
        packet.rhrh = 45.0f;
        packet.iotData2 = 0.0f;

        unsigned char status = 0;

        if (packet.descentSpeed < 12.0f || packet.descentSpeed > 14.0f) {
            status |= (1 << 0);
        }

        if (packet.iotData1 < 6.0f || packet.iotData1 > 8.0f) {
            status |= (1 << 1);
        }

        if (packet.pressure1 == 0.0f) {
            status |= (1 << 2);
        }

        if (packet.gpsLatitude == 0.0f && packet.gpsLongitude == 0.0f) {
            status |= (1 << 3);
        }

        if (separationOccurred == 0) {
            status |= (1 << 4);
        }

        if (filterWorking == 0) {
            status |= (1 << 5);
        }

        packet.packetStatus = status;

        unsigned char *ptr = (unsigned char *)&packet;
        unsigned int sum = 0;

        for(int i=0; i < sizeof(TelemetryPacket)-1; i++) {
            sum += ptr[i];
        }
        packet.checksum = sum % 256;

        ssize_t sentBytes = sendto(sockfd, &packet, sizeof(TelemetryPacket), 0,
                                    (const struct sockaddr *)&targetAddr, sizeof(targetAddr));

        if (sentBytes < 0) {
             perror("Send failed");
        } else {
             printf("Packet: %d | Status: %d | Speed: %.2f | Alt: %.2f\n",
                    counter, packet.packetStatus, packet.descentSpeed, packet.altitude1);
        }

        counter++;
        sleep(1);
    }

    close(sockfd);
    return 0;
}