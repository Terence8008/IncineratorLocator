// views/ResultView.jsx
export default function ResultView({ result }) {
  return (
    <div className="p-4 bg-white shadow border rounded mt-2">
      <h2 className="font-bold text-xl">Prediction Result</h2>
      <p className="mt-2">Suitability Score: <strong>{result.score}</strong></p>

      <h3 className="mt-3 font-semibold">Extracted Features</h3>
      <pre className="bg-gray-100 p-3 rounded text-sm mt-1">
        {JSON.stringify(result.features, null, 2)}
      </pre>
    </div>
  );
}
