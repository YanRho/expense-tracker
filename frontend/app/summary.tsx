import React, { useEffect, useState } from "react";
import { View, Text, ActivityIndicator, StyleSheet } from "react-native";
import api from "../api/client";

type SummaryData = {
  total_income: number;
  total_expense: number;
  net: number;
};

export default function SummaryScreen() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/insights/summary/")
      .then((res) => setSummary(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <ActivityIndicator style={{ marginTop: 100 }} size="large" />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Summary Insights</Text>
      <View style={styles.card}>
        <Text style={styles.label}>Total Income:</Text>
        <Text style={styles.income}>${summary?.total_income.toFixed(2)}</Text>

        <Text style={styles.label}>Total Expense:</Text>
        <Text style={styles.expense}>${summary?.total_expense.toFixed(2)}</Text>

        <Text style={styles.label}>Net:</Text>
        <Text style={styles.net}>${summary?.net.toFixed(2)}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, flex: 1, backgroundColor: "#fff" },
  title: { fontSize: 24, fontWeight: "bold", marginBottom: 20 },
  card: { backgroundColor: "#f9f9f9", padding: 20, borderRadius: 10 },
  label: { fontSize: 16, marginTop: 10 },
  income: { fontSize: 18, color: "green" },
  expense: { fontSize: 18, color: "red" },
  net: { fontSize: 20, fontWeight: "bold", marginTop: 10 },
});
