import { SourceDetailPage } from '@/components/pages/SourceDetailPage';

interface SourcePageProps {
  params: Promise<{
    sourceName: string;
  }>;
}

export default async function SourcePage({ params }: SourcePageProps) {
  const { sourceName } = await params;
  const decodedSourceName = decodeURIComponent(sourceName);
  
  return <SourceDetailPage sourceName={decodedSourceName} />;
}