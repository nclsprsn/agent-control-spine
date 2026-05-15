export default function CatalogPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Catalog</h1>
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search capabilities and tools..."
          className="w-full max-w-md border border-gray-300 rounded-md px-4 py-2 text-sm"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-lg font-semibold mb-4">Capabilities</h2>
          <p className="text-gray-400 text-sm">No capabilities registered yet.</p>
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-4">Tools</h2>
          <p className="text-gray-400 text-sm">No tools registered yet.</p>
        </div>
      </div>
    </div>
  );
}
