import React from 'react';
import type { Field } from '@shared/farm';
import { MapContainer, TileLayer, Polygon, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface FieldMapProps {
  fields: Field[];
  centerLat?: number;
  centerLng?: number;
}

const FieldMap: React.FC<FieldMapProps> = ({ fields, centerLat = 9.0123, centerLng = 38.7654 }) => {
  // Safe default center if no fields are provided
  const mapCenter: [number, number] = fields.length > 0 && fields[0].centroid_geojson 
    ? [fields[0].centroid_geojson.coordinates[1], fields[0].centroid_geojson.coordinates[0]] // GeoJSON is [lng, lat]
    : [centerLat, centerLng];

  return (
    <div className="w-full h-full relative z-0 relative rounded-xl overflow-hidden border border-gray-200">
      <MapContainer 
        center={mapCenter} 
        zoom={15} 
        style={{ height: '100%', width: '100%', zIndex: 10 }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {fields.map((field) => {
          if (!field.boundary_geojson || !field.boundary_geojson.coordinates) return null;
          
          // Convert GeoJSON polygon coordinates [lng, lat] to Leaflet coordinates [lat, lng]
          const positions = field.boundary_geojson.coordinates[0].map(
            (coord) => [coord[1], coord[0]] as [number, number]
          );

          return (
            <Polygon 
              key={field.id} 
              positions={positions} 
              pathOptions={{ fillColor: '#22c55e', color: '#166534', weight: 2, fillOpacity: 0.4 }}
            >
              <Tooltip sticky direction="top" className="font-bold">
                {field.name} ({field.area_ha} ha)
              </Tooltip>
            </Polygon>
          );
        })}
      </MapContainer>
      
      {/* Fallback overlay warning if offline */}
      <div className="absolute top-2 left-2 z-[20] bg-white/90 backdrop-blur pb-1 px-2 rounded text-xs font-bold text-gray-700 shadow flex items-center gap-1">
        <span className="w-2 h-2 rounded-full bg-green-500"></span> GPS Active
      </div>
    </div>
  );
};

export default FieldMap;
