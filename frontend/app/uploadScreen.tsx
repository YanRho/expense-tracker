import React from "react";
import { View, Text, Button, Alert } from "react-native";
import * as DocumentPicker from "expo-document-picker";
import api from "../api/client";

export default function UploadScreen() {
    const handleUpload = async () => {
        try {
            const result = await DocumentPicker.getDocumentAsync({
                type: "text/csv", 
                copyToCacheDirectory: true,
            });

            if (result.canceled) return;

            const file = { 
                uri: result.assets?.[0].uri || "",
                name: result.assets?.[0].name || "file.csv",
                type: "text/csv",
            };

            const formData = new FormData();
            formData.append("file", file as any);

            const response = await api.post("/upload-csv", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            Alert.alert("Success", response.data.message || "File uploaded successfully!");
        } catch (err: any) {
            console.error(err);
            Alert.alert("Error", "Failed to upload file. Please try again.");
        }
    };

    return (
        <View style={{ padding: 20 }}>
            <Text style={{ fontSize: 18, marginBottom: 10 }}>Upload CSV File</Text>
            <Button title="Pick and Upload CSV" onPress={handleUpload} />
        </View>
    );
}